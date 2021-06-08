"""
dsw7@sfu.ca

Convex hull plots for mapped bridges.
"""

from os import path
from json import load
from matplotlib import pyplot

INPUT_FILENAME = 'n_3_bridge_transformations.json'
OUTPUT_FILE_PHE = 'phe_bridges_3d.png'
OUTPUT_FILE_TYR = 'tyr_bridges_3d.png'
OUTPUT_FILE_TRP = 'trp_bridges_3d.png'
DIM_XYZ_NEG = -7
DIM_XYZ_POS =  7
PLOT_DOTS_PER_INCH = 300
FIGSIZE_WIDTH_HEIGHT_INCHES = (5, 5)


class FilterData:

    def __init__(self):
        path_to_input = path.join(path.dirname(path.dirname(__file__)), 'data', INPUT_FILENAME)
        print('> Reading data from file {}'.format(path_to_input))

        with open(path_to_input) as f:
            self.raw_data = load(f)

    def get_phe_data(self) -> list:
        phe_coordinates = []

        for document in self.raw_data:
            for entry in document:
                if 'PHE' in entry:
                    phe_coordinates.append(document[entry])

        return list(zip(*phe_coordinates))

    def get_tyr_data(self) -> list:
        tyr_coordinates = []

        for document in self.raw_data:
            for entry in document:
                if 'TYR' in entry:
                    tyr_coordinates.append(document[entry])

        return list(zip(*tyr_coordinates))

    def get_trp_data(self) -> list:
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
        print('> Exporting {}'.format(filepath))
        pyplot.savefig(filepath, dpi=PLOT_DOTS_PER_INCH)

    def render_tyr_convex_hull(self, data: list, filepath: str) -> None:
        figure = pyplot.figure(figsize=FIGSIZE_WIDTH_HEIGHT_INCHES)
        ax_tyr = figure.add_subplot(111, projection='3d')
        pyplot.setp(ax_tyr, **self.limits)
        ax_tyr.scatter(*data, c='r', marker='o', s=1)
        ax_tyr.plot(*self.ce_sd_cg_frame, c='k', lw=2)
        ax_tyr.set_title('TYR bridges')
        print('> Exporting {}'.format(filepath))
        pyplot.savefig(filepath, dpi=PLOT_DOTS_PER_INCH)

    def render_trp_convex_hull(self, data: list, filepath: str) -> None:
        figure = pyplot.figure(figsize=FIGSIZE_WIDTH_HEIGHT_INCHES)
        ax_trp = figure.add_subplot(111, projection='3d')
        pyplot.setp(ax_trp, **self.limits)
        ax_trp.scatter(*data, c='r', marker='o', s=1)
        ax_trp.plot(*self.ce_sd_cg_frame, c='k', lw=2)
        ax_trp.set_title('TRP bridges')
        print('> Exporting {}'.format(filepath))
        pyplot.savefig(filepath, dpi=PLOT_DOTS_PER_INCH)


def main() -> None:
    filter_handle = FilterData()
    data_phe = filter_handle.get_phe_data()
    data_tyr = filter_handle.get_tyr_data()
    data_trp = filter_handle.get_trp_data()

    rootdir = path.dirname(__file__)
    png_convex_hull_phe = path.join(rootdir, OUTPUT_FILE_PHE)
    png_convex_hull_tyr = path.join(rootdir, OUTPUT_FILE_TYR)
    png_convex_hull_trp = path.join(rootdir, OUTPUT_FILE_TRP)

    plotter = RenderConvexHulls()
    plotter.render_phe_convex_hull(data_phe, png_convex_hull_phe)
    plotter.render_tyr_convex_hull(data_tyr, png_convex_hull_tyr)
    plotter.render_trp_convex_hull(data_trp, png_convex_hull_trp)

if __name__ == '__main__':
    main()
