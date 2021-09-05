"""
dsw7@sfu.ca

Groupby convex hull plots for mapped bridges.
"""

import sys
import logging
from os import path
from json import load
from re import findall, compile
from itertools import groupby

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s %(message)s'
)

INPUT_FILENAME = 'n_3_bridge_transformations.json'
PATTERN_AROMATICS = compile('(PHE|TYR|TRP)')
EXIT_FAILURE = 1


class GroupPipeline:

    def __init__(self) -> None:

        path_to_input = path.join(path.dirname(path.dirname(__file__)), 'data', INPUT_FILENAME)
        logging.info('Reading data from file %s', path_to_input)

        try:
            with open(path_to_input) as f:
                self.raw_data = load(f)
        except FileNotFoundError:
            logging.exception('Could not open file!')
            sys.exit(EXIT_FAILURE)

        logging.info('Found %i entries in file', len(self.raw_data))
        self.grouped_data = {}

    def insert_sort_key(self) -> None:
        logging.info('Inserting a sort key into each entry')

        for row in self.raw_data:
            """
            1. Keys inside row          -> MET95TYR68PHE99TYR90code
            2. MET95TYR68PHE99TYR90code -> ['TYR', 'PHE', 'TYR']
            3. ['TYR', 'PHE', 'TYR']    -> ['PHE', 'TYR', 'TYR']
            4. ['PHE', 'TYR', 'TYR']    -> PHETYRTYR
            """
            row['key'] = ''.join(sorted(findall(PATTERN_AROMATICS, ''.join(row.keys()))))

    def sort_raw_data(self) -> None:
        logging.info('Sorting raw data')
        self.raw_data.sort(key=lambda k: k['key'])

    def group_data(self) -> None:
        logging.info('Grouping data')

        for group, data in groupby(self.raw_data, lambda k: k['key']):
            self.grouped_data[group] = list(data)

    def collect_statistics(self) -> None:
        logging.info('Analyzing data:')

        count = 0
        logging.info('{:>5} {:>15} {:>15} {:>15}'.format('Row', 'Group', 'Count', 'Cumulative Sum'))

        for u, group in enumerate(self.grouped_data, 1):
            group_size = len(self.grouped_data[group])
            count += group_size
            logging.info('{:>5} {:>15} {:>15} {:>15}'.format(u, group, group_size, count))

        logging.info('')

    def remove_outliers(self) -> None:
        logging.info('Removing outliers')

        bad_groups = []
        for group in self.grouped_data:
            if len(group) != 9:
                logging.warning('The following group will be removed from the dataset: %s', group)
                logging.warning('The size of the dataset will change by -%s', len(self.grouped_data[group]))
                bad_groups.append(group)

        for group in bad_groups:
            del self.grouped_data[group]

    def executor_main(self) -> None:
        self.insert_sort_key()
        self.sort_raw_data()
        self.group_data()
        self.collect_statistics()
        self.remove_outliers()
        self.collect_statistics()


def main() -> None:
    filter_handle = GroupPipeline()
    filter_handle.executor_main()

if __name__ == '__main__':
    main()
