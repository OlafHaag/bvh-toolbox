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

""" Convert CSV files back to a BVH file.
You'll need 3 CSV files for now:
* Hierarchy file
* Rotation file
* Translation file
Theoretically, it should be possible to just use hierarchy and translation data only to reconstruct the bvh file.
But that means solving the problem of acute versus obtuse angles and decomposing that to rotation order.
Ain't nobody got time for that! :D
"""

import os
import sys
import argparse

import numpy as np

from bvhtoolbox import BvhTree


def get_hierarchy_data(hierarchy_file):
    """ Get data on the skeleton's hierarchy from CSV file.
    
    :param hierarchy_file: CSV source file containing hierarchy. Columns: joint, parent, offset.x, offset.y, offset.z
    :type hierarchy_file: str
    :return: Dictionary with skeleton hierarchy. {name: {'parent': str, 'offset': array, 'children': list}
    :rtype: dict
    """
    try:
        rec_array = np.recfromcsv(hierarchy_file, encoding='UTF-8')
    except OSError as e:
        print("ERROR:", e)
        raise
    offsets = rec_array[['offsetx', 'offsety', 'offsetz']].copy().view((float, 3))
    joint_info = {j[0]: {'parent': j[1], 'offset': offsets[i], 'children': []} for i, j in enumerate(rec_array)}
    update_children(joint_info)
    input_is_sane = hierarchy_sanity_check(joint_info)
    return joint_info
    

def update_children(nodes):
    """ Fills the children property of joints."""
    for node, properties in nodes.items():
        parent = properties['parent']
        try:
            p_props = nodes[parent]
        except KeyError:
            if not parent:  # Root has no parent.
                continue
            raise ValueError("ERROR: Parent of {} cannot be found in the hierarchy definition!".format(node))
        p_children = p_props['children']
        p_children.append(node)
        p_props.update({'children': p_children})


def hierarchy_sanity_check(nodes):
    """ Checks for errors in the skeleton's hierarchy.
    
    :param nodes: Dictionary with skeleton hierarchy.
    :type nodes: dict
    :return: True if no error occurred.
    :rtype: bool
    """
    for node, properties in nodes.items():
        parent = properties['parent']
        if node == parent:
            raise ValueError("ERROR: Joint {} cannot be parent of itself!".format(node))
        if parent in properties['children']:
            raise ValueError("Impossible cyclic relation detected for joints {} and {}!".format(node, parent))
        if parent and parent not in nodes.keys():
            raise ValueError("ERROR: Parent of joint {} cannot be found in the hierarchy definition!".format(node))
    # No error occurred.
    return True
    
    
def get_transform_data(transforms_file):
    """Returns column names as list and data as numpy array.
    
    :param transforms_file: CSV source file holding transformation data like rotations or translations.
    :type: str
    :return: A list of column names and the data.
    :rtype: tuple
    """
    # Numpy is losing case of column names when using np.recfromcsv().
    # Read 1st line as header manually instead and use genfromtxt() to get data.
    try:
        data = np.genfromtxt(transforms_file, delimiter=",", skip_header=1)
    except OSError as e:
        print("ERROR:", e)
        raise
    with open(transforms_file, 'rb') as file_handle:
        columns = file_handle.readline().strip().decode("utf-8").split(sep=',')
        
    return columns, data
    

def df_to_joints(df):
    """ Return joint names from list of degrees of freedom. List of joint names is sorted alphabetically."""
    joints = list(set((x.split('.')[0] for x in df if df != 'time')))
    joints.sort()
    return joints
    
    
def get_frame_time(time_steps):
    """ Compute average frame time.
    
    :param time_steps: 1D array with cumulative frame times.
    :type time_steps: numpy.ndarray
    :return: The average length of each frame in seconds.
    :rtype: float
    """
    if len(time_steps.shape) != 1:
        raise ValueError("ERROR: Time series must be a 1D array.")
    frame_time = time_steps[-1]/(len(time_steps) - 1)  # Need to ignore the first frame (0).
    return frame_time

    
def get_angle_radians(vec1, vec2, acute=True):
    """Returns angle in radians between 2 vectors."""
    radians = np.arccos(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    if acute:
        return radians
    else:
        # Return obtuse angle.
        return 2 * np.pi - radians


def csv2bvh(*args, **kwargs):
    raise NotImplementedError


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Convert BVH file to CSV table format.""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s 0.1a1')
    parser.add_argument("-o", "--out", type=str, default='', help="Destination file path for BVH file.\n"
                                                             "If no destination path is given, CSV file path is used.")
    parser.add_argument("-s", "--scale", type=float, default=1.0,
                        help="Scale factor for root translation and offset values. In case you have to switch from "
                             "centimeters to meters or vice versa.")
    parser.add_argument("hierarchy.csv", type=str, help="CSV source file needed to convert to BVH.")
    parser.add_argument("location.csv", type=str, help="CSV source file needed to convert to BVH.")
    parser.add_argument("rotation.csv", type=str, help="CSV source file needed to convert to BVH.")
    args = vars(parser.parse_args(argv))
    hierarchy_src = args['hierarchy.csv']
    location_src = args['location.csv']
    rotation_src = args['rotation.csv']
    dst_file_path = args['out']
    scale = args['scale']
    
    success = csv2bvh(hierarchy_src, location_src, rotation_src, dst_file_path)
    return success


if __name__ == "__main__":
    exit_code = int(not main())
    sys.exit(exit_code)
