# MIT License
#
# Copyright (c) 2018 Olaf Haag
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from itertools import repeat

import numpy as np
import transforms3d as t3d

from . import BvhTree

# Axis sequences for Euler angles.
_NEXT_AXIS = [1, 2, 0, 1]

# Map axes strings to/from tuples of inner axis, parity.
_AXES2TUPLE = {
    'xyz': (0, 0), 'xyx': (0, 0), 'xzy': (0, 1),
    'xzx': (0, 1), 'yzx': (1, 0), 'yzy': (1, 0),
    'yxz': (1, 1), 'yxy': (1, 1), 'zxy': (2, 0),
    'zxz': (2, 0), 'zyx': (2, 1), 'zyz': (2, 1)}


def prune(a, epsilon=0.00000001):
    """Sets absolute values smaller than epsilon to 0.
    It does this in-place on the input array.

    :param a: array
    :type a: numpy.ndarray
    :param epsilon: threshold
    :type epsilon: float
    """
    a[np.abs(a) < epsilon] = 0.0
    

def get_motion_data(bvh_tree):
    """Returns frames as numpy array.
    
    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :return: Values for all channels for all frames.
    :rtype: numpy.ndarray
    """
    frames = np.array(bvh_tree.frames).astype(float)
    return frames


def set_motion_data(bvh_tree, data):
    """Sets the frames of bvh structure to values in data.
    
    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param data: 2d array of float values. rows are frames, columns are channels.
    :type data: numpy.ndarray
    """
    bvh_tree.frames = data.astype(str).tolist()
    

def reorder_axes(xyz, axes='zxy'):
    """Takes an input array in xyz order and re-arranges it to given axes order.

    :param xyz: array with x,y,z order.
    :param axes: output order for Euler conversions respective to axes.
    :return: array in axes order.
    :rtype: numpy.ndarray
    """
    if xyz.shape[-1] != 3 or len(xyz.shape) > 2:
        print("ERROR: Frames must be 1D or 2D array with 3 columns for x,y,z axes!")
        raise ValueError
    # If the output order is the same as the input, do not reorder.
    if axes == 'xyz':
        return xyz
    
    i, j, k = _get_reordered_indices(axes)
    # 1-D arrays.
    if len(xyz.shape) == 1:
        res = np.array([xyz[i], xyz[j], xyz[k]])
    # 2-D arrays: multiple frames.
    elif len(xyz.shape) == 2:
        # Todo: is something like data[:,1], data[:,2] = data[:,2], data[:,1].copy() faster/more efficient?
        res = np.array([xyz[:, i], xyz[:, j], xyz[:, k]]).T
    return res


def _get_reordered_indices(rotation_order):
    """Returns indices for converting 'xyz' rotation order to given rotation order.
    
    :param rotation_order: Rotation order to convert to.
    :type rotation_order: str
    :return: Indices for getting from xyz to given axes rotation order.
    :rtype: tuple
    """
    try:
        firstaxis, parity = _AXES2TUPLE[rotation_order]
    except KeyError:
        print("Rotation order must be one of {}.".format(', '.join(_AXES2TUPLE.keys())))
        raise
    i = firstaxis
    j = _NEXT_AXIS[i + parity]
    k = _NEXT_AXIS[i - parity + 1]
    return i, j, k


def get_euler_angles(bvh_tree, joint_name, axes='zxy'):
    """Return Euler angles in degrees for joint in all frames.

    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param joint_name: Name of the joint
    :type joint_name: str
    :param axes: The order in which to return the angles. Usually that's the joint's channel order.
    :return: Euler angles in order of axes (frames x 3).
    :rtype: numpy.ndarray
    """
    euler_xyz = np.array(bvh_tree.frames_joint_channels(joint_name, ['Xrotation', 'Yrotation', 'Zrotation'],
                                                        value=0.0))  # For missing channels. bvh > v3.0!
    euler_ordered = reorder_axes(euler_xyz, axes)
    return euler_ordered


def get_quaternions(bvh_tree, joint_name, axes='rzxz'):
    """Get the wxyz quaternion representations of a joint for all frames.
    
    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param joint_name: Name of the joint.
    :type joint_name: str
    :param axes: The order in which to parse the Euler angles. Usually that's the joint's channel order.
    :type axes: str
    :return: quaternion wxyz for all frames (frames x 4).
    :rtype: numpy.ndarray
    """
    eulers = np.radians(get_euler_angles(bvh_tree, joint_name, axes[1:]))
    quaternions = np.array(list(map(t3d.euler.euler2quat, eulers[:, 0], eulers[:, 1], eulers[:, 2], repeat(axes))))
    #prune(quaternions)
    return quaternions
    
    
def get_rotation_matrices(bvh_tree, joint_name, axes='rzxz'):
    """Read the Euler angles of a joint in order given by axes and return it as rotation matrices for all frames.

    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param joint_name: Name of the joint.
    :type joint_name: str
    :param axes: The order in which to return the angles. Usually that's the joint's channel order.
    :type axes: str
    :return: rotation matrix (frames x 3 x 3)
    :rtype: numpy.ndarray
    """
    eulers = np.radians(get_euler_angles(bvh_tree, joint_name, axes[1:]))
    matrices = np.array(list(map(t3d.euler.euler2mat, eulers[:, 0], eulers[:, 1], eulers[:, 2], repeat(axes))))
    prune(matrices)
    return matrices


def get_translations(bvh_tree, joint_name):
    """Get the xyz translation of a joint for all frames.
    
    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param joint_name: Name of the joint.
    :type joint_name: str
    :return: translations xyz for all frames (frames x 3).
    :rtype: numpy.ndarray
    """
    translations = np.array(bvh_tree.frames_joint_channels(joint_name, ['Xposition', 'Yposition', 'Zposition'],
                                                           value=0.0))  # For missing channels. bvh > v3.0!
    return translations
    
    
def get_affines(bvh_tree, joint_name, axes='rzxz'):
    """Read the transforms of a joint with rotation in order given by axes and return it as an affine matrix.

    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param joint_name: Name of the joint.
    :type joint_name: str
    :param axes: The order in which to return the angles. Usually that's the joint's channel order.
    :type axes: str
    :return: affine matrix (frames x 4 x 4)
    :rtype: numpy.ndarray
    """
    translations = get_translations(bvh_tree, joint_name)
    rot_matrices = get_rotation_matrices(bvh_tree, joint_name, axes=axes)
    
    affine_matrices = np.array(list(map(t3d.affines.compose,
                                        translations,
                                        rot_matrices,
                                        np.ones((bvh_tree.nframes, 3)))))
    return affine_matrices


if __name__ == '__main__':
    # Testing
    bvh_filepath = "example_files/source/walk01.bvh"
    with open(bvh_filepath) as file_handle:
        mocap = BvhTree(file_handle.read())
    
    mat_hips = get_affines(mocap, 'Hips')
    mat_left_hand = get_affines(mocap, 'LeftHand')
