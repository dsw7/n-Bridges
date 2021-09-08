"""
Unit testing the transformation algorithm
"""

# pylint: disable=C0103

from copy import deepcopy
from typing import Tuple
from pytest import approx
from numpy import random, array
from pyquaternion import Quaternion
from data.transformer import Transformer


class Triangle:
    """
    Generate a simple triangle for unit testing the Transformer class
    """

    def __init__(self) -> None:
        self.triangle = array([
            [0.00, 0.00, 0.00],
            [1.00, 0.00, 0.00],
            [0.00, 1.00, 0.00]
        ])

    def translate(self, dx: float, dy: float, dz: float) -> None:
        """ Translate the triangle in x, y, z direction """
        self.triangle = self.triangle + array([dx, dy, dz])

    def rotate(self, degrees: float, axis: Tuple[float, float, float]) -> None:
        """ Rotate the triangle about axis """
        quaternion = Quaternion(axis=axis, degrees=degrees)
        self.triangle[0] = quaternion.rotate(self.triangle[0])
        self.triangle[1] = quaternion.rotate(self.triangle[1])
        self.triangle[2] = quaternion.rotate(self.triangle[2])

    def get(self) -> Tuple[float, float, float]:
        return self.triangle[0], self.triangle[1], self.triangle[2]


def test_translate_octant_I() -> None:
    triangle = Triangle()

    # Anti-transform a mocked triangle
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(1, 1, 1)
    triangle_intermediate = triangle.get()

    # Then undo the anti-transformation using the Transformer class
    triangle_end = Transformer(*triangle_intermediate).get_base()
    assert sum(sum(triangle_start)) == approx(sum(sum(triangle_end)))

def test_translate_octant_II() -> None:
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(-1, 1, 1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    assert sum(sum(triangle_start)) == approx(sum(sum(triangle_end)))

def test_translate_octant_III() -> None:
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(-1, -1, 1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    assert sum(sum(triangle_start)) == approx(sum(sum(triangle_end)))

def test_translate_octant_IV() -> None:
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(1, -1, 1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    assert sum(sum(triangle_start)) == approx(sum(sum(triangle_end)))

def test_translate_octant_V() -> None:
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(1, 1, -1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    assert sum(sum(triangle_start)) == approx(sum(sum(triangle_end)))

def test_translate_octant_VI() -> None:
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(-1, 1, -1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    assert sum(sum(triangle_start)) == approx(sum(sum(triangle_end)))

def test_translate_octant_VII() -> None:
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(-1, -1, -1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    assert sum(sum(triangle_start)) == approx(sum(sum(triangle_end)))

def test_translate_octant_VIII() -> None:
    triangle = Triangle()
    triangle_start = deepcopy(triangle.get())
    triangle.rotate(degrees=random.uniform(low=-180, high=180), axis=(1.00, 1.00, 0.00))
    triangle.translate(1, -1, -1)
    triangle_intermediate = triangle.get()
    triangle_end = Transformer(*triangle_intermediate).get_base()
    assert sum(sum(triangle_start)) == approx(sum(sum(triangle_end)))
