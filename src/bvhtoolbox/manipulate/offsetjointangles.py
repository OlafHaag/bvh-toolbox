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
import sys
import csv
import argparse

import numpy as np
import transforms3d as t3d

from .. import get_pkg_version
from .. import BvhTree
from .. import get_quaternions, get_motion_data, set_motion_data


def add_angle_offsets(bvh_tree, angle_offsets):
    """Add rotation to joints in bvh_tree.

    :param bvh_tree: BVH structure
    :type bvh_tree: bvhtree.BvhTree
    :param angle_offsets: A dictionary containing joint names as keys and euler angles in degrees as values.
    The order of the euler angles needs to be the same as the channel order for this joint in the BVH file.
    If not all 3 rotation channels are present for a joint, the missing channels will get appended.
    :type angle_offsets: dict
    """
    if not angle_offsets:
        print("WARNING: No rotation offsets. Aborting.")
        return
    
    frames = get_motion_data(bvh_tree)
    # Convert the given euler angles to quaternions.
    for joint_name, angle_values in angle_offsets.items():
        try:
            joint = bvh_tree.get_joint(joint_name)
        except LookupError:
            print("WARNING: joint {} not found.".format(joint_name))
            continue
            
        channel_names = bvh_tree.joint_channels(joint_name)
        # Find CHANNELS BvhNode.
        channel_node = joint.children[1]
        for channel in ['Xrotation', 'Yrotation', 'Zrotation']:
            if channel not in channel_names:
                channel_names.append(channel)
                # Joint gets a new channel
                channel_node.value.append(channel)
                channel_node.value[1] = str(int(channel_node.value[1]) + 1)
                # Insert new channel into frames.
                insert_idx = bvh_tree.get_joint_channels_index(joint_name) + bvh_tree.get_joint_channel_index(joint_name, channel)
                frames = np.insert(frames, insert_idx, 0.0, axis=1)  # Initialize with 0.
        channel_order = 's' + ''.join([channel[:1].lower() for channel in channel_names if channel.endswith("rotation")])
        angle_offset_quat = t3d.euler.euler2quat(*np.radians(angle_values), axes=channel_order)
        joint_angles = get_quaternions(bvh_tree, joint_name, axes=channel_order)
        new_angles = np.degrees([t3d.euler.quat2euler(t3d.quaternions.qmult(q, angle_offset_quat), axes=channel_order) for q in joint_angles])
        # Replace frames with new values.
        channels_idx = bvh_tree.get_joint_channels_index(joint_name)
        rot_channels_idx = channels_idx + bvh_tree.get_joint_channel_index(joint_name, channel_names[0])
        frames[:, rot_channels_idx: rot_channels_idx+3] = new_angles
    set_motion_data(bvh_tree, frames)


def bvhfile_offset_angles(src_filepath, angle_offsets, dst_filepath=None):
    """
    :param src_filepath: File path for BVH source.
    :type src_filepath: str
    :param angle_offsets: A dictionary containing joint names as keys and euler angles in degrees as values.
    The order of the euler angles needs to be the same as the channel order for this joint in the BVH file.
    If not all 3 rotation channels are present for a joint, the missing channels will get appended.
    :type angle_offsets: dict
    :param dst_filepath: File path for destination BVH file.
    :type dst_filepath: str
    :return: If reading and writing the BVH files was successful or not.
    :rtype: bool
    """
    if not angle_offsets:
        print("WARNING: No rotation offsets. Aborting processing of file", src_filepath)
        return False
    
    try:
        with open(src_filepath) as file_handle:
            mocap = BvhTree(file_handle.read())
    except OSError as e:
        print("ERROR:", e)
        return False
    
    add_angle_offsets(mocap, angle_offsets)
    
    if not dst_filepath:
        dst_filepath = src_filepath
    res = mocap.write_file(dst_filepath)
    return res


def load_angle_offsets(csv_path):
    """Load additive euler angles from CSV file.
    header: joint, i, j, k
    Order of x,y,z values must match order of rotation channels in BVH file. If the order is zxy then i=z, j=x, k=y.
    
    :param csv_path: Path to CSV file containing values.
    :type csv_path: str
    :return: Angle offsets as dictionary.
    :rtype: dict
    """
    angle_offsets = dict()
    try:
        with open(csv_path) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                angle_offsets[row['joint']] = tuple(float(row[i]) for i in 'ijk')
    except OSError as e:
        print("ERROR:", e)
    except ValueError as e:
        print("ERROR: Reading angle values failed.", e)
    return angle_offsets


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Add rotations as offsets to joints in BVH files.""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s v{}'.format(get_pkg_version()))
    parser.add_argument("input.bvh", nargs='+', type=str, help="BVH files.")
    parser.add_argument("angles.csv", type=str, help="CSV file containing the mapping of joint names to euler angles.")
    parser.add_argument("-o", "--out", nargs='*', type=str, help="Destination file paths for modified BVH files.\n"
                                                                 "If no out path is given, or list is shorter than\n"
                                                                 "input files, BVH files are overwritten.")
    args = vars(parser.parse_args(argv))
    src_files_paths = args['input.bvh']
    dst_files_paths = args['out']
    if not dst_files_paths:
        dst_files_paths = list()
    angles_file_path = args['angles.csv']
    angles = load_angle_offsets(angles_file_path)

    res = list()
    for i, bvh_file in enumerate(src_files_paths):
        # There could be less destination paths or None.
        if i >= len(dst_files_paths):
            dst_file = None
        else:
            dst_file = dst_files_paths[i]
        res.append(bvhfile_offset_angles(bvh_file, angles, dst_file))

    num_errors = len(res) - sum(res)
    if num_errors > 0:
        print("ERROR: {} files could not be processed.".format(num_errors))
    return False if num_errors else True


if __name__ == "__main__":
    exit_code = int(not main())
    sys.exit(exit_code)
