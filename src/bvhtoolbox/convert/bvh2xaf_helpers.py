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

"""
This collection of function is for debugging purposes.
The functions are meant to be used in an interactive session to evaluate conversion results.
Requires 'dev' extras when installing bvhtoolbox.
"""
import numpy as np
import transforms3d as t3d
from sympy import Matrix

from .. import BvhTree

# Axis sequences for Euler angles.
_NEXT_AXIS = [1, 2, 0, 1]

# Map axes strings to/from tuples of inner axis, parity.
_AXES2TUPLE = {
    'xyz': (0, 0), 'xyx': (0, 0), 'xzy': (0, 1),
    'xzx': (0, 1), 'yzx': (1, 0), 'yzy': (1, 0),
    'yxz': (1, 1), 'yxy': (1, 1), 'zxy': (2, 0),
    'zxz': (2, 0), 'zyx': (2, 1), 'zyz': (2, 1)}


def reorder_axes(xyz, axes='xyz'):
    """Takes an input array in xyz order and re-arranges it to given axes order.
    
    :param xyz: array with x,y,z order.
    :param axes: output order for Euler conversions respective to axes.
    :return: array in axes order.
    :rtype: numpy.ndarray
    """
    firstaxis, parity = _AXES2TUPLE[axes]
    i = firstaxis
    j = _NEXT_AXIS[i + parity]
    k = _NEXT_AXIS[i - parity + 1]
    return np.array([xyz[i], xyz[j], xyz[k]])
    
    
def prune(a, epsilon=0.00000001):
    """Sets values smaller than epsilon to 0.
    It does this in-place on the input array.
    
    :param a: array
    :param epsilon: threshold
    """
    a[np.abs(a) < epsilon] = 0.0


def string2quat(xaf_str):
    """Takes quaternion string (xyzw) and converts it to quaternion array (wxyz).
    
    :param xaf_string: space delimited xyzw quaternion
    :type xaf_string: str
    :return: quaternion (wxyz)
    :rtype: numpy.ndarray
    """
    quat = np.fromstring(xaf_str, sep=' ')
    quat = np.roll(quat, shift=1)
    prune(quat)
    return quat


def quat2string(quat):
    """Takes quaternion (wxyz) and outputs string in xyzw order.
    
    :param quat: quaternion in wxyz order.
    :type quat: numpy.ndarray
    :return: string representation
    :rtype: str
    """
    quat = np.roll(quat, shift=-1)
    s = np.array_str(quat)[1:-1]
    return s


def string2mat(xaf_string):
    """Returns rotation matrix for a string of quaternions (xyzw).
    
    :param xaf_string: space delimited xyzw quaternion
    :type xaf_string: str
    :return: rotation matrix (3x3)
    :rtype: numpy.ndarray
    """
    quat = string2quat(xaf_string)
    rot_mat = t3d.quaternions.quat2mat(quat)
    return rot_mat


def mat2string(rot_mat):
    """Converts a rotation matrix to string representation of a quaternion (xyzw).
    
    :param rot_mat: rotation matrix
    :type rot_mat: numpy.ndarray
    :return: quaternion string representation of rotation matrix
    :rtype: str
    """
    quat = t3d.quaternions.mat2quat(rot_mat)
    s = quat2string(quat)
    return s


def mat2affine(rot_mat, translation=None):
    """Converts a rotation matrix to string representation of a quaternion (xyzw).
    
    :param rot_mat: rotation matrix (3x3)
    :type rot_mat: numpy.ndarray
    :param translation: translation with x,y,z components
    :type translation: numpy.ndarray
    :return: affine matrix with scaling 1. (4x4)
    :rtype: numpy.ndarray
    """
    if not translation:
        translation = np.zeros(3)
    affine = t3d.affines.compose(translation, rot_mat, np.ones(3))
    return affine


def mat2euler(rot_mat, axes='rzxz'):
    """Return rotation matrix as Euler angles in order of axes.
    
    
    """
    return np.degrees(t3d.euler.mat2euler(rot_mat, axes=axes))


def string2euler(xaf_string, axes='rzxz'):
    """Convert XAF quaternion string to Euler angles.
    
    :param xaf_string: space delimited xyzw quaternion
    :type xaf_string: str
    :param axes: The order in which to return the angles. Usually that's the joint's channel order.
    :type axes: str
    :return: Euler angles
    :rtype: numpy.ndarray
    """
    mat = string2mat(xaf_string)
    euler = mat2euler(mat, axes)
    return euler


def string2affine(xaf_string, translation_str=None):
    """Converts a string representation of a quaternion (xyzw) to an affine matrix (4x4).
    
    :param xaf_string: space delimited xyzw quaternion
    :type xaf_string: str
    :param translation_str: translation string with x y z components
    :type translation_str: str
    :return: affine matrix with scaling 1. (4x4)
    :rtype: numpy.ndarray
    """
    if not translation_str:
        t = np.zeros(0)
    else:
        t = np.fromstring(translation_str, sep=' ')
    rot_mat = string2mat(xaf_string)
    affine = mat2affine(rot_mat, t)
    return affine


def get_bvh_tree(file_path):
    """Parse a BVH file and return it as Bvh object.
    
    :param file_path: file path to BVH file.
    :type file_path: str
    :return: BVH tree
    :rtype: bvhtree.BvhTree
    """
    with open(file_path) as file_handle:
        bvh_tree = BvhTree(file_handle.read())
    return bvh_tree


def channels2axes(bvh_tree, joint_name):
    """Get the channels/rotation axes order for a joint and return it as a string."""
    channels = bvh_tree.joint_channels(joint_name)
    axes = ''.join([s[0] for s in channels if 'rotation' in s.lower()]).lower()
    return axes


def euler_str2quat(euler_string, in_order='zxy', conversion_order='rzxz'):
    """Takes a space delinmited string of Euler angles and converts it to quaternion representation.
    
    :param euler_string: 3 space delimited values for angles
    :param in_order: Channel order in BVH file. The order of the values coming in.
    :param conversion_order: The order that the angles are meant to represent, e.g. 'rzxz'.
    :return: quaternion (wxyz)
    :rtype: numpy.ndarray
    """
    eulers_deg = np.fromstring(euler_string, sep=' ')
    eulers_xyz = np.array([eulers_deg[in_order.lower().index(i)] for i in 'xyz'])
    ordered_euler = reorder_axes(eulers_xyz, axes=conversion_order[1:])
    eulers_rad = np.radians(ordered_euler)
    quat = t3d.euler.euler2quat(*eulers_rad, axes=conversion_order)
    return quat


def get_euler(bvh_tree, joint_name, frame=0, axes='zxy'):
    """Return Euler angles in degrees for joint at frame.
    
    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param joint_name: Name of the joint
    :type joint_name: str
    :param frame: frame to return
    :type frame: int
    :param axes: The order in which to return the angles. Usually that's the joint's channel order.
    :type axes: str
    :return: Euler angles in order of axes.
    :rtype: numpy.ndarray
    """
    euler_xyz = np.array(bvh_tree.frame_joint_channels(frame, joint_name, ['Xrotation', 'Yrotation', 'Zrotation'],
                                                       value=0.0))  # For missing channels. bvh > v3.0!
    euler_ordered = reorder_axes(euler_xyz, axes)
    return euler_ordered
    
    
def joint2quat(bvh_tree, joint_name, frame=0, axes='rzxz'):
    """Read the Euler angles of a joint in order given by axes and return it as quaternions.
    
    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param joint_name: Name of the joint.
    :type joint_name: str
    :param frame: The frame to return.
    :type frame: int
    :param axes: The order in which to return the angles. Usually that's the joint's channel order.
    :type axes: str
    :return: quaterion (wxyz)
    :rtype: numpy.ndarray
    """
    euler_ordered = np.radians(get_euler(bvh_tree, joint_name, frame, axes[1:]))
    quat = t3d.euler.euler2quat(*euler_ordered, axes=axes)
    return quat
    

def joint2mat(bvh_tree, joint_name, frame=0, axes='rzxz'):
    """Read the Euler angles of a joint in order given by axes and return it as rotation matrix.

    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param joint_name: Name of the joint.
    :type joint_name: str
    :param frame: The frame to return.
    :type frame: int
    :param axes: The order in which to return the angles. Usually that's the joint's channel order.
    :type axes: str
    :return: rotation matrix (3x3)
    :rtype: numpy.ndarray
    """
    euler_ordered = np.radians(get_euler(bvh_tree, joint_name, frame, axes[1:]))
    mat = t3d.euler.euler2mat(*euler_ordered, axes=axes)
    return mat


def joint2affine(bvh_tree, joint_name, frame=0, axes='rzxz'):
    """Read the tranforms of a joint with rotation in order given by axes and return it as an affine matrix.

    :param bvh_tree: BVH structure.
    :type bvh_tree: bvhtree.BvhTree
    :param joint_name: Name of the joint.
    :type joint_name: str
    :param frame: The frame to return.
    :type frame: int
    :param axes: The order in which to return the angles. Usually that's the joint's channel order.
    :type axes: str
    :return: affine matrix (4x4)
    :rtype: numpy.ndarray
    """
    translation = np.array(bvh_tree.frame_joint_channels(frame, joint_name, ['Xposition', 'Yposition', 'Zposition'],
                                                         value=0.0))  # For missing channels. bvh > v3.0!
    euler_ordered = np.radians(get_euler(bvh_tree, joint_name, frame, axes[1:]))
    rot_mat = t3d.euler.euler2mat(*euler_ordered, axes=axes)
    affine = t3d.affines.compose(translation, rot_mat, np.ones(3))
    return affine
    
    
def get_transform_matrix(a, b):
    """Get transformation matrix p for converting a to b, such that B = P**-1 * A * P. Matrices A and B are similar.
    F = G**-1 * A * G
    F = H**1 * B * H
    P = G * H**-1
    :param a: Matrix A
    :param b: Matrix B
    :return: P
    """
    g, _ = Matrix(a).jordan_form()
    h, _ = Matrix(b).jordan_form()
    p = g * h.inv()
    return np.array(p)
