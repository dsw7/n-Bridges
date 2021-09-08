"""
Convex hull plots for mapped bridges.
"""

import sys
import logging
from os import path, makedirs
from json import load
from matplotlib import pyplot

INPUT_FILENAME = 'n_3_bridge_transformations.json'
OUTPUT_FILE_PHE = 'phe_bridges_3d.png'
OUTPUT_FILE_TYR = 'tyr_bridges_3d.png'
OUTPUT_FILE_TRP = 'trp_bridges_3d.png'
DIM_XYZ_NEG = -7
DIM_XYZ_POS =  7
PLOT_DOTS_PER_INCH = 100
FIGSIZE_WIDTH_HEIGHT_INCHES = (5, 5)
EXIT_FAILURE = 1

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s %(message)s'
)


class FilterData:

    def __init__(self) -> None:
        path_to_json = path.join(path.dirname(path.dirname(__file__)), 'data', INPUT_FILENAME)
        logging.info('Reading data from file %s', path_to_json)

        try:
            with open(path_to_json) as f:
                self.raw_data = load(f)
        except FileNotFoundError:
            logging.exception('Could not open file!')
            sys.exit(EXIT_FAILURE)

    def get_phe_data(self) -> list:
        logging.info('Isolating phenylalanine data from original dataset')
        phe_coordinates = []

        for document in self.raw_data:
            for entry in document:
                if 'PHE' in entry:
                    phe_coordinates.append(document[entry])

        return list(zip(*phe_coordinates))

    def get_tyr_data(self) -> list:
        logging.info('Isolating tyrosine data from original dataset')
        tyr_coordinates = []

        for document in self.raw_data:
            for entry in document:
                if 'TYR' in entry:
                    tyr_coordinates.append(document[entry])

        return list(zip(*tyr_coordinates))

    def get_trp_data(self) -> list:
        logging.info('Isolating tryptophan data from original dataset')
        trp_coordinates = []

        for document in self.raw_data:
            for entry in document:
                if 'TRP' in entry:
                    trp_coordinates.append(document[entry])

        return list(zip(*trp_coordinates))


class RenderConvexHulls:

    def __init__(self) -> None:
        self.ce_sd_cg_frame = self._render_ce_sd_cg_frame()
        self.limits = {
            'xlim': (DIM_XYZ_NEG, DIM_XYZ_POS),
            'ylim': (DIM_XYZ_NEG, DIM_XYZ_POS),
            'zlim': (DIM_XYZ_NEG, DIM_XYZ_POS),
            'xlabel': 'x',
            'ylabel': 'y',
            'zlabel': 'z'
        }

    @staticmethod
    def _render_ce_sd_cg_frame() -> list:
        approximate_coords_cg = [-0.25, 1.80, 0.00]
        approximate_coords_sd = [0.00, 0.00, 0.00]
        approximate_coords_ce = [1.75, 0.00, 0.00]
        approximate_all = [
            approximate_coords_cg,
            approximate_coords_sd,
            approximate_coords_ce
        ]
        return list(zip(*approximate_all))

    def render_phe_convex_hull(self, data: list, filepath: str) -> None:
        figure = pyplot.figure(figsize=FIGSIZE_WIDTH_HEIGHT_INCHES)
        ax_phe = figure.add_subplot(111, projection='3d')
        pyplot.setp(ax_phe, **self.limits)
        ax_phe.scatter(*data, c='r', marker='o', s=1)
        ax_phe.plot(*self.ce_sd_cg_frame, c='k', lw=2)
        ax_phe.set_title('PHE bridges')
        logging.info('Exporting %s', filepath)
        pyplot.savefig(filepath, dpi=PLOT_DOTS_PER_INCH)

    def render_tyr_convex_hull(self, data: list, filepath: str) -> None:
        figure = pyplot.figure(figsize=FIGSIZE_WIDTH_HEIGHT_INCHES)
        ax_tyr = figure.add_subplot(111, projection='3d')
        pyplot.setp(ax_tyr, **self.limits)
        ax_tyr.scatter(*data, c='r', marker='o', s=1)
        ax_tyr.plot(*self.ce_sd_cg_frame, c='k', lw=2)
        ax_tyr.set_title('TYR bridges')
        logging.info('Exporting %s', filepath)
        pyplot.savefig(filepath, dpi=PLOT_DOTS_PER_INCH)

    def render_trp_convex_hull(self, data: list, filepath: str) -> None:
        figure = pyplot.figure(figsize=FIGSIZE_WIDTH_HEIGHT_INCHES)
        ax_trp = figure.add_subplot(111, projection='3d')
        pyplot.setp(ax_trp, **self.limits)
        ax_trp.scatter(*data, c='r', marker='o', s=1)
        ax_trp.plot(*self.ce_sd_cg_frame, c='k', lw=2)
        ax_trp.set_title('TRP bridges')
        logging.info('Exporting %s', filepath)
        pyplot.savefig(filepath, dpi=PLOT_DOTS_PER_INCH)


def main() -> None:
    filter_handle = FilterData()
    data_phe = filter_handle.get_phe_data()
    data_tyr = filter_handle.get_tyr_data()
    data_trp = filter_handle.get_trp_data()

    rootdir = path.join(path.dirname(__file__), 'plots')
    makedirs(rootdir, exist_ok=True)

    png_convex_hull_phe = path.join(rootdir, OUTPUT_FILE_PHE)
    png_convex_hull_tyr = path.join(rootdir, OUTPUT_FILE_TYR)
    png_convex_hull_trp = path.join(rootdir, OUTPUT_FILE_TRP)

    plotter = RenderConvexHulls()
    plotter.render_phe_convex_hull(data_phe, png_convex_hull_phe)
    plotter.render_tyr_convex_hull(data_tyr, png_convex_hull_tyr)
    plotter.render_trp_convex_hull(data_trp, png_convex_hull_trp)

    logging.info('Done!')

if __name__ == '__main__':
    main()
