"""
dsw7@sfu.ca

This script is a hack for getting 3-bridges from the following .csv:
    -- low_redundancy_delimiter_list.csv
The script was used to generate the following MongoDB database.collection:
    -- ma.n_3_bridge_transformations
And this database.collection pair was then mongoexported to the json file:
    -- n_3_bridge_transformations.json

I repeat... this script is a hack. The metaromatic.ma2 module no longer exists.
This module was superseded by the MetAromatic project:
    -- https://github.com/dsw7/MetAromatic

"""

from itertools import groupby
from re import findall, search
from metaromatic.ma2 import MetAromatic
from numpy import array
from pymongo import MongoClient
from transformer import Transformer

DB = 'ma'
COL = 'n_3_bridge_transformations'
PORT = 27017
HOST = 'localhost'
LOW_REDUNDANCY_STRUCTURES_CSV = 'low_redundancy_delimiter_list.csv'
ANGLE = 360.00
CUTOFF = 6.00
CHAIN = 'A'
CLIENT = MongoClient(port=PORT, host=HOST)


class ThreeBridges():

    def __init__(self, code):
        self.code = code
        ma = MetAromatic(code=code, angle=ANGLE, cutoff=CUTOFF, chain=CHAIN)
        ma.met_aromatic()
        self.raw_data = ma.methionines + ma.phenylalanines + ma.tyrosines + ma.tryptophans
        self.bridges = ma.bridging_interactions(n=4)

    def bridge_exists(self):
        """ Check if entry contains a bridge """
        if not self.bridges:
            return False
        return True

    def remove_inverse_bridges(self):
        """ Remove bridges of form MET - ARO - MET - ARO """
        self.outgoing = []
        for bridge in self.bridges:
            string = ''.join(bridge)
            if len(findall('MET', string)) == 1:
                self.outgoing.append(bridge)

    def cluster_bridge_data(self):
        """ Get raw data corresponding only to bridges """
        self.raw_data_bridges = []
        for bridge in self.outgoing:
            dict_bridge = {}
            for residue in bridge:
                position = search(r'\d+', residue).group(0)
                dict_bridge[residue] = [row for row in self.raw_data if row[5] == position]
            self.raw_data_bridges.append(dict_bridge)

    def isolate_relevant_coordinates(self):
        """ Get only the relevant coordinates needed for quaternion change of base """
        self.isolated_coordinates = []
        for bridge in self.raw_data_bridges:
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
                    else:
                        pass
            self.isolated_coordinates.append(list_bridge)

    def isolate_tetrahedrons(self):
        """ Compute methionine / aromatic centroid tetrahedrons """
        self.tetrahedrons = []
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
                        aromatic, key,
                        0.5 * (coord_1 + coord_2)
                    ))
            self.tetrahedrons.append(tetrahedron)

    def transform_tetrahedrons(self):
        """ Map the methionine / aromatic centroid tetrahedrons to origin """
        self.transformations = []
        for tetrahedron in self.tetrahedrons:
            transformed = {}
            for residue in tetrahedron:  # transform the CG-SD-CE frame
                if residue[0] == 'MET':
                    transform = Transformer(*residue[2:5])  # cast to list for mongodb
                    methionine_base = [arr.tolist() for arr in transform.get_base()]
                    transformed[''.join(residue[0:2])] = methionine_base

            for residue in tetrahedron:  # transform the satellite coordinates
                if residue[0] != 'MET':
                    transformed[''.join(residue[0:2])] = transform.rotate_satellite(residue[2]).tolist()

            self.transformations.append(transformed)


def get_test_pdb_codes(filename):
    with open(filename) as f:
        codes = [line.strip('\n') for line in f]
    return codes

def main():
    codes = get_test_pdb_codes(LOW_REDUNDANCY_STRUCTURES_CSV)
    for count, code in enumerate(codes, 1):
        print(count, code)
        try:
            obj = ThreeBridges(code=code)
            if obj.bridge_exists():
                obj.remove_inverse_bridges()
                obj.cluster_bridge_data()
                obj.isolate_relevant_coordinates()
                obj.isolate_tetrahedrons()
                obj.transform_tetrahedrons()
                for tetrahedron in obj.transformations:
                    tetrahedron['code'] = code
                    CLIENT[DB][COL].insert(tetrahedron)
            else:
                print('No bridges.')
        except Exception as exception:
            print('An exception has occurred:')
            print(exception)

if __name__ == '__main__':
    main()
