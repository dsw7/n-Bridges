"""
dsw7@sfu.ca
Algorithm for performing full CH3-S-CH2 mapping to xy plane.
"""

# pylint: disable=C0103

from math import atan2
from typing import Tuple
from pyquaternion import Quaternion
from numpy import (
    linalg,
    arccos,
    dot,
    degrees,
    cross,
    array,
    array_equal
)

PRECISION_COMP = 5

def vector_angle(u: array, v: array) -> float:
    numerator = dot(u, v)
    denominator = linalg.norm(v) * linalg.norm(u)
    return degrees(arccos(numerator / denominator))


class Transformer:

    """
    Map a triangle with coordinates (A, B, C) to the xy plane:
    [1] We make A -> (0, 0, 0)
    [2] We make AB colinear with x-axis
    [3] We make ABC coplanar with xy

    This class returns a set of quaternion attributes that can be used to
    transform a set of satellite points alongside ABC.
    """

    def __init__(self, A: array, B: array, C: array) -> None:

        self.D = A - A
        self.E = B - A
        self.F = C - A

        # Snap to x-axis
        # -----------------
        alpha = vector_angle(self.E, (1, 0, 0))
        axis_first_rotation = cross(self.E, (1, 0, 0))

        if array_equal(axis_first_rotation, array([0, 0, 0])):
            self.first_quaternion = 1
            G = self.D
            H = self.E
            I = self.F
        else:
            self.first_quaternion = Quaternion(axis=-axis_first_rotation, degrees=-alpha)
            G = self.first_quaternion.rotate(self.D)
            H = self.first_quaternion.rotate(self.E)
            I = self.first_quaternion.rotate(self.F)

        # Rotate triangle into xy plane
        # -----------------
        theta = degrees(atan2(I[2], I[1]))  # Treat yz as if it is xy and apply into atan2
        self.second_quaternion = Quaternion(axis=(1, 0, 0), degrees=-theta)
        self.J = self.second_quaternion.rotate(G)
        self.K = self.second_quaternion.rotate(H)
        self.L = self.second_quaternion.rotate(I)

        # Need for dealing with satellites
        self.A = A

    def get_base(self) -> Tuple[array, array, array]:
        """ Return the base which is mapped to xy plane """
        return self.J, self.K, self.L

    @staticmethod
    def check_pre_post_transform_dets(triangle: array, triangle_transformed: array) -> None:
        """ Confirm that volume of the transformee is identical post transformation """
        assert linalg.det(triangle).round(PRECISION_COMP) == linalg.det(triangle_transformed).round(PRECISION_COMP)

    def rotate_satellite(self, satellite_point: array) -> array:
        """ Rotate out any satellite points using the existing quaternions """

        composition = self.second_quaternion * self.first_quaternion
        satellite_point = satellite_point - self.A
        satellite_rotated = composition.rotate(satellite_point)

        self.check_pre_post_transform_dets([self.E, self.F, satellite_point], [self.K, self.L, satellite_rotated])
        return satellite_rotated
