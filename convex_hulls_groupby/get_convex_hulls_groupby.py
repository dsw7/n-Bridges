"""
Groupby convex hull plots for mapped bridges.
"""

import sys
import logging
from os import path, makedirs
from json import load, dump
from itertools import groupby
from re import (
    findall,
    compile,
    match
)
from matplotlib import pyplot

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s %(message)s'
)

ROOT = path.dirname(__file__)
INPUT_FILENAME = 'n_3_bridge_transformations.json'
PATTERN_AROMATICS = compile('(PHE|TYR|TRP)')
EXIT_FAILURE = 1
DIM_XYZ_NEG = -7
DIM_XYZ_POS =  7
PLOT_DOTS_PER_INCH = 100
FIGSIZE_WIDTH_HEIGHT_INCHES = (5, 5)

def render_ce_sd_cg_frame() -> list:
    approximate_coords_cg = [-0.25, 1.80, 0.00]
    approximate_coords_sd = [0.00, 0.00, 0.00]
    approximate_coords_ce = [1.75, 0.00, 0.00]
    approximate_all = [
        approximate_coords_cg,
        approximate_coords_sd,
        approximate_coords_ce
    ]
    return list(zip(*approximate_all))


class GroupPipeline:

    def __init__(self) -> None:

        path_to_json = path.join(path.dirname(ROOT), 'data', INPUT_FILENAME)
        logging.info('Reading data from file %s', path_to_json)

        try:
            with open(path_to_json) as f:
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

    def dump_data(self) -> None:
        path_to_dump = path.join(ROOT, 'dump')
        makedirs(path_to_dump, exist_ok=True)

        for group in self.grouped_data:
            filepath = path.join(path_to_dump, '{}.json'.format(group.lower()))
            logging.info('Dumping %s sorted data to %s', group, filepath)

            with open(filepath, 'w') as f:
                dump(self.grouped_data[group], f, indent=4)

    def executor_main(self) -> dict:
        self.insert_sort_key()
        self.sort_raw_data()
        self.group_data()
        self.collect_statistics()
        self.remove_outliers()
        self.collect_statistics()
        self.dump_data()
        return self.grouped_data


class RenderConvexHulls:

    def __init__(self, group: str, grouped_data: list) -> None:
        logging.info('Processing group %s', group)

        self.grouped_data = grouped_data
        self.group = group
        self.coordinates = []

        self.path_to_plots = path.join(ROOT, 'plots')
        makedirs(self.path_to_plots, exist_ok=True)

    def isolate_aromatic_coordinates(self) -> None:
        logging.info('Isolating aromatic coordinates from grouped data')

        for entry in self.grouped_data:
            for key in entry:
                if match(PATTERN_AROMATICS, key):
                    self.coordinates.append(entry[key])

        self.coordinates = list(zip(*self.coordinates))

    def render_convex_hull(self) -> None:
        logging.info('Rendering convex hull for %s bridges', self.group)

        figure = pyplot.figure(figsize=FIGSIZE_WIDTH_HEIGHT_INCHES)
        ax = figure.add_subplot(111, projection='3d')

        limits = {
            'xlim': (DIM_XYZ_NEG, DIM_XYZ_POS),
            'ylim': (DIM_XYZ_NEG, DIM_XYZ_POS),
            'zlim': (DIM_XYZ_NEG, DIM_XYZ_POS),
            'xlabel': 'x',
            'ylabel': 'y',
            'zlabel': 'z'
        }

        pyplot.setp(ax, **limits)
        ax.scatter(*self.coordinates, c='r', marker='o', s=1)
        ax.plot(*render_ce_sd_cg_frame(), c='k', lw=2)
        ax.set_title('{} bridges'.format(self.group))

        filepath = path.join(self.path_to_plots, '{}_bridges_3d.png'.format(self.group.lower()))
        logging.info('Exporting %s', filepath)
        pyplot.savefig(filepath, dpi=PLOT_DOTS_PER_INCH)

    def executor_main(self) -> None:
        self.isolate_aromatic_coordinates()
        self.render_convex_hull()


def main() -> None:
    pipeline = GroupPipeline()
    processed = pipeline.executor_main()

    for group in processed:
        plotter = RenderConvexHulls(group, processed[group])
        plotter.executor_main()

    logging.info('Done!')

if __name__ == '__main__':
    main()
