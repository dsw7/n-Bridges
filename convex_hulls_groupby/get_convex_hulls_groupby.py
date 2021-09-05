"""
dsw7@sfu.ca

Groupby convex hull plots for mapped bridges.
"""

import logging
from os import path
from json import load

logging.basicConfig(level=logging.DEBUG)

INPUT_FILENAME = 'n_3_bridge_transformations.json'


class FilterData:

    def __init__(self) -> None:

        path_to_input = path.join(path.dirname(path.dirname(__file__)), 'data', INPUT_FILENAME)
        logging.info('> Reading data from file {}'.format(path_to_input))

        try:
            with open(path_to_input) as f:
                self.raw_data = load(f)
        except FileNotFoundError:
            logging.exception('Could not open file!')


def main() -> None:
    filter_handle = FilterData()

if __name__ == '__main__':
    main()
