import pkg_resources

from .bvh import Bvh, BvhNode
from .bvhtree import BvhTree
from .bvhtransforms import get_affines,\
                           get_euler_angles, \
                           get_quaternions,\
                           get_translations, \
                           get_rotation_matrices,\
                           get_motion_data, \
                           set_motion_data,\
                           prune


def get_pkg_version():
    version = pkg_resources.get_distribution(__package__).version
    return version


__version__ = get_pkg_version()
