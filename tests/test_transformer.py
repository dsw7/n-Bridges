"""
dsw7@sfu.ca
Unit testing the transformation algorithm
"""

# -----------------------------------------------------------------------------
# Dependencies
# -----------------------------------------------------------------------------
from copy import deepcopy
from pytest import approx
from numpy import random, array
from pyquaternion import Quaternion
from transformer import Transformer


# -----------------------------------------------------------------------------
# A simple triangle
# -----------------------------------------------------------------------------
class Triangle:
    """ Generate a triangle for unit testing the Transformer class. """
    def __init__(self):
        self.triangle = array([
            [0.00, 0.00, 0.00],
            [1.00, 0.00, 0.00],
            [0.00, 1.00, 0.00]
        ])

    def translate(self, dx, dy, dz):
        """ Translate the triangle in x, y, z direction """
        self.triangle = self.triangle + array([dx, dy, dz])

    def rotate(self, degrees=0, axis=(1.00, 0.00, 0.00)):
        """ Rotate the triangle about axis """
        quaternion = Quaternion(axis=axis, degrees=degrees)
        self.triangle[0] = quaternion.rotate(self.triangle[0])
        self.triangle[1] = quaternion.rotate(self.triangle[1])
        self.triangle[2] = quaternion.rotate(self.triangle[2])

    def get(self):
        return self.triangle[0], self.triangle[1], self.triangle[2]


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
def test_translate_octant_I():
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(1, 1, 1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    sum_start = sum(sum(triangle_start))
    sum_end = sum(sum(triangle_end))
    assert sum_start == approx(sum_end)


def test_translate_octant_II():
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(-1, 1, 1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    sum_start = sum(sum(triangle_start))
    sum_end = sum(sum(triangle_end))
    assert sum_start == approx(sum_end)


def test_translate_octant_III():
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(-1, -1, 1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    sum_start = sum(sum(triangle_start))
    sum_end = sum(sum(triangle_end))
    assert sum_start == approx(sum_end)


def test_translate_octant_IV():
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(1, -1, 1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    sum_start = sum(sum(triangle_start))
    sum_end = sum(sum(triangle_end))
    assert sum_start == approx(sum_end)


def test_translate_octant_V():
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(1, 1, -1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    sum_start = sum(sum(triangle_start))
    sum_end = sum(sum(triangle_end))
    assert sum_start == approx(sum_end)


def test_translate_octant_VI():
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(-1, 1, -1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    sum_start = sum(sum(triangle_start))
    sum_end = sum(sum(triangle_end))
    assert sum_start == approx(sum_end)


def test_translate_octant_VII():
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(-1, -1, -1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    sum_start = sum(sum(triangle_start))
    sum_end = sum(sum(triangle_end))
    assert sum_start == approx(sum_end)


def test_translate_octant_VIII():
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(1, -1, -1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    sum_start = sum(sum(triangle_start))
    sum_end = sum(sum(triangle_end))
    assert sum_start == approx(sum_end)
