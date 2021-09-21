#!/usr/bin/env python3

"""
This script is a hack for getting 3-bridges from the following .csv:
    -- low_redundancy_delimiter_list.csv
The script was used to generate the following MongoDB database.collection:
    -- ma.n_3_bridge_transformations
And this database.collection pair was then mongoexported to the json file:
    -- n_3_bridge_transformations.json

I repeat... this script is a hack. The metaromatic.ma2 module no longer exists.
The metaromatic.ma2 module was superseded by the MetAromatic project:
    -- https://github.com/dsw7/MetAromatic
"""

import logging
from itertools import groupby
from typing import Union
from re import findall, search
from MetAromatic.core.pair import MetAromatic
from numpy import array
from pymongo import MongoClient
from networkx import Graph, connected_components
from transformer import Transformer

LOW_REDUNDANCY_STRUCTURES_CSV = 'low_redundancy_delimiter_list.csv'
MONGO_DATABASE = 'ma2'
MONGO_COLLECTION = 'n_3_bridge_transformations'
MONGO_TCP_PORT = 27017
MONGO_HOST = 'localhost'
CUTOFF_ANGLE = 360.00
CUTOFF_DISTANCE = 6.00
CHAIN = 'A'
MODEL = 'cp'
VERTICES = 4
EXIT_FAILURE = 1

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s %(asctime)s %(message)s'
)


class CustomThreeBridgeGetter:

    def __init__(self, code: str) -> None:

        self.code = code
        self.raw_coordinate_data = []
        self.pairs = []
        self.joined_pairs = set()
        self.bridges = []

    def run_met_aromatic(self) -> bool:

        arguments = {
            'cutoff_distance': CUTOFF_DISTANCE,
            'cutoff_angle': CUTOFF_ANGLE,
            'chain': CHAIN,
            'model': MODEL
        }

        ma = MetAromatic(**arguments)
        self.pairs = ma.get_met_aromatic_interactions(self.code)

        if self.pairs['exit_code'] == EXIT_FAILURE:
            return False

        self.raw_coordinate_data.extend(ma.transport['met_coordinates'])
        self.raw_coordinate_data.extend(ma.transport['phe_coordinates'])
        self.raw_coordinate_data.extend(ma.transport['tyr_coordinates'])
        self.raw_coordinate_data.extend(ma.transport['trp_coordinates'])

        return True

    def get_joined_pairs(self) -> bool:
        for result in self.pairs['results']:
            pair = (
                '{}{}'.format(result['aromatic_residue'], result['aromatic_position']),
                'MET{}'.format(result['methionine_position'])
            )
            self.joined_pairs.add(pair)

    def get_bridges(self) -> bool:
        graph = Graph()
        graph.add_edges_from(self.joined_pairs)

        components = list(connected_components(graph))

        if not components:
            return False

        for bridge in components:
            if len(bridge) == VERTICES:
                self.bridges.append(bridge)

        if not self.bridges:
            return False

        return True

    def get_bridging_interactions(self) -> Union[bool, list]:

        if not self.run_met_aromatic():
            return False

        self.get_joined_pairs()

        if not self.get_bridges():
            return False

        return self.bridges


class ThreeBridges:

    def __init__(self, code: str) -> None:
        self.code = code
        self.raw_bridges = []
        self.bridges_without_inverts = []
        self.raw_coordinate_data = []
        self.raw_coordinate_data_bridges = []
        self.isolated_coordinates = []
        self.tetrahedrons = []
        self.transformations = []

    def remove_inverse_bridges(self) -> None:
        """ Remove bridges of form MET - ARO - MET - ARO """

        for bridge in self.raw_bridges:
            string = ''.join(bridge)
            if len(findall('MET', string)) == 1:
                self.bridges_without_inverts.append(bridge)

    def cluster_bridge_data(self) -> None:
        """ Get raw data corresponding only to bridges """

        for bridge in self.bridges_without_inverts:
            dict_bridge = {}

            for residue in bridge:
                position = search(r'\d+', residue).group(0)
                dict_bridge[residue] = [row for row in self.raw_coordinate_data if row[5] == position]

            self.raw_coordinate_data_bridges.append(dict_bridge)

    def isolate_relevant_coordinates(self) -> None:
        """ Get only the relevant coordinates needed for quaternion change of base """

        for bridge in self.raw_coordinate_data_bridges:
            list_bridge = []

            for amino_acid in bridge:
                for row in bridge.get(amino_acid):
                    if row[3] == 'MET' and row[2] == 'SD':
                        list_bridge.append(row)
                    elif row[3] == 'MET' and row[2] == 'CG':
                        list_bridge.append(row)
                    elif row[3] == 'MET' and row[2] == 'CE':
                        list_bridge.append(row)
                    elif row[3] == 'PHE' and row[2] == 'CG':
                        list_bridge.append(row)
                    elif row[3] == 'PHE' and row[2] == 'CZ':
                        list_bridge.append(row)
                    elif row[3] == 'TYR' and row[2] == 'CG':
                        list_bridge.append(row)
                    elif row[3] == 'TYR' and row[2] == 'CZ':
                        list_bridge.append(row)
                    elif row[3] == 'TRP' and row[2] == 'CD2':
                        list_bridge.append(row)
                    elif row[3] == 'TRP' and row[2] == 'CH2':
                        list_bridge.append(row)

            self.isolated_coordinates.append(list_bridge)

    def isolate_tetrahedrons(self) -> None:
        """ Compute methionine / aromatic centroid tetrahedrons """

        for bridge in self.isolated_coordinates:
            tetrahedron = []

            for key, residues in groupby(bridge, key=lambda x: x[5]):
                list_residues = list(residues)

                if list_residues[0][3] == 'MET':
                    tetrahedron.append((
                        'MET', key,
                        array(list_residues[0][6:9]).astype(float),
                        array(list_residues[1][6:9]).astype(float),
                        array(list_residues[2][6:9]).astype(float)
                    ))
                else:
                    aromatic = list_residues[0][3]
                    coord_1 = array(list_residues[0][6:9]).astype(float)
                    coord_2 = array(list_residues[1][6:9]).astype(float)
                    tetrahedron.append((
                        aromatic, key, 0.5 * (coord_1 + coord_2)
                    ))

            self.tetrahedrons.append(tetrahedron)

    def transform_tetrahedrons(self) -> None:
        """ Map the methionine / aromatic centroid tetrahedrons to origin """

        for tetrahedron in self.tetrahedrons:
            transformed = {}

            for residue in tetrahedron:  # Transform the CG-SD-CE frame
                if residue[0] == 'MET':
                    transform = Transformer(*residue[2:5])
                    methionine_base = [arr.tolist() for arr in transform.get_base()]
                    transformed[''.join(residue[0:2])] = methionine_base

            for residue in tetrahedron:  # Transform the satellite coordinates
                if residue[0] != 'MET':
                    transformed[''.join(residue[0:2])] = transform.rotate_satellite(residue[2]).tolist()

            self.transformations.append(transformed)

    def executor_main(self) -> Union[bool, list]:
        bridge_getter = CustomThreeBridgeGetter(self.code)

        self.raw_bridges = bridge_getter.get_bridging_interactions()
        if not self.raw_bridges:
            return False

        self.remove_inverse_bridges()
        if not self.bridges_without_inverts:
            return False

        self.raw_coordinate_data = bridge_getter.raw_coordinate_data
        self.cluster_bridge_data()
        self.isolate_relevant_coordinates()
        self.isolate_tetrahedrons()
        self.transform_tetrahedrons()

        return self.transformations


def main() -> None:
    client = MongoClient(port=MONGO_TCP_PORT, host=MONGO_HOST)

    with open(LOW_REDUNDANCY_STRUCTURES_CSV) as f:
        codes = [line.strip('\n') for line in f]

    for count, code in enumerate(codes, 1):
        try:
            getter = ThreeBridges(code)
            transformations = getter.executor_main()

            if not transformations:
                logging.info('%i %s - No bridges', count, code)
                continue

            logging.info('%i %s - Found bridges', count, code)

            for transformation in transformations:
                transformation['code'] = code
                client[MONGO_DATABASE][MONGO_COLLECTION].insert(transformation)

        except Exception:
            logging.exception('An exception has occurred:')

if __name__ == '__main__':
    main()
