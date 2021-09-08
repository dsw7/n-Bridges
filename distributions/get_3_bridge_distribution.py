"""
* David Weber *

Plot a hbar chart depicting distribution of all 10 possible 3-bridge
aromatic permutations
"""

import sys
import logging
from os import path, makedirs
from re import match
from collections import Counter
from json import load
from matplotlib import pyplot

INPUT_FILENAME = 'n_3_bridge_transformations.json'
OUTPUT_FILENAME = 'distribution.png'
VERTICAL_IMAGE_SIZE_INCHES = 3
HORIZONTAL_IMAGE_SIZE_INCHES = 3
IMAGE_DPI = 250
EXIT_FAILURE = 1

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s %(message)s'
)


class ComputeDistribution:

    def __init__(self):
        path_to_json = path.join(path.dirname(path.dirname(__file__)), 'data', INPUT_FILENAME)
        logging.info('Reading data from file %s', path_to_json)

        try:
            with open(path_to_json) as f:
                self.raw_data = load(f)
        except FileNotFoundError:
            logging.exception('Could not open file!')
            sys.exit(EXIT_FAILURE)

        self.all_residues = []
        self.bridges = []
        self.bridges_without_numerics = []
        self.counts = None

    def filter_in_all_residues(self):
        for entry in self.raw_data:
            row = list(entry.keys())
            row.remove('code')
            self.all_residues.append(row)

    def remove_methionines_from_cluster(self):
        for entry in self.all_residues:
            self.bridges.append(
                [residue for residue in entry if 'MET' not in residue]
            )

    def strip_out_residue_position_number(self):
        for raw_bridge in self.bridges:

            bridge = []
            for aromatic in raw_bridge:
                retstr = match('[A-Z]+', aromatic)

                if retstr:  # 5JNQ and 3GLJ are buggy and retstr will be NoneType
                    bridge.append(retstr.group(0))

            if len(bridge) == 3:  # 5JNQ and 3GLJ are buggy
                self.bridges_without_numerics.append(bridge)

    def get_bridge_counts(self):
        bridges_sorted = [
            tuple(sorted(i)) for i in self.bridges_without_numerics
        ]
        self.counts = Counter(bridges_sorted).most_common()

    def execute_pipeline(self):
        self.filter_in_all_residues()
        self.remove_methionines_from_cluster()
        self.strip_out_residue_position_number()
        self.get_bridge_counts()
        return self.counts


def main():
    distributions = ComputeDistribution().execute_pipeline()

    pyplot.rcdefaults()
    _, ax = pyplot.subplots(
        figsize=(HORIZONTAL_IMAGE_SIZE_INCHES, VERTICAL_IMAGE_SIZE_INCHES)
    )

    categories, counts = [], []
    for count in distributions:
        categories.append(r'{' + ', '.join(count[0]) + r'}')
        counts.append(count[1])

    vertical_positions = range(len(categories))
    ax.barh(vertical_positions, counts, align='center', edgecolor='k', lw=0.5, color='r')
    ax.set_yticks(vertical_positions)
    ax.set_yticklabels(categories, size=10)
    ax.set_xlabel('Counts', size=10)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.invert_yaxis()

    rootdir = path.join(path.dirname(__file__), 'plots')
    makedirs(rootdir, exist_ok=True)

    export_file = path.join(rootdir, OUTPUT_FILENAME)
    logging.info('Exporting file to %s', export_file)
    pyplot.savefig(export_file, dpi=IMAGE_DPI, bbox_inches='tight')

    logging.info('Done!')

if __name__ == '__main__':
    main()
