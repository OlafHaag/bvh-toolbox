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

""" Convert animation data in BVH file to CSV format.
Rotation data and position are separate output files.
The first line is a header with each degree of freedom as a column.
The first column is the frame for the data in that row.
The second column is the time of the frame in seconds.
The degrees of freedom in the joints are written in the order they appear in the BVH file as channels.
"""

import os
import sys
import argparse
from multiprocessing import freeze_support

import numpy as np
import transforms3d as t3d

from .. import get_pkg_version
from .. import BvhTree
from .. import get_affines
from .multiprocess import get_bvh_files, parallelize


def write_joint_rotations(bvh_tree, filepath):
    """Write joints' rotation data to a CSV file.

    :param bvh_tree: BVH tree that holds the data.
    :type bvh_tree: BvhTree
    :param filepath: Destination file path for CSV file.
    :type filepath: str
    :return: If the write process was successful or not.
    :rtype: bool
    """
    time_col = np.arange(0, (bvh_tree.nframes - 0.5)*bvh_tree.frame_time, bvh_tree.frame_time)[:, None]
    data_list = [time_col]
    header = ['time']
    for joint in bvh_tree.get_joints():
        channels = [channel for channel in bvh_tree.joint_channels(joint.name) if channel[1:] == 'rotation']
        header.extend(['{}.{}'.format(joint.name, channel[:1].lower()) for channel in channels])
        data_list.append(np.array(bvh_tree.frames_joint_channels(joint.name, channels)))
        
    data = np.concatenate(data_list, axis=1)
    try:
        np.savetxt(filepath, data, header=','.join(header), fmt='%10.5f', delimiter=',', comments='')
        return True
    except IOError as e:
        print("ERROR({}): Could not write to file {}.\n"
              "Make sure you have writing permissions.\n".format(e.errno, filepath))
        return False
    

def write_joint_positions(bvh_tree, filepath, scale=1.0, end_sites=False):
    """Write joints' world positional data to a CSV file.
    
    :param bvh_tree: BVH tree that holds the data.
    :type bvh_tree: BvhTree
    :param filepath: Destination file path for CSV file.
    :type filepath: str
    :param scale: Scale factor for root position and offset values.
    :type scale: float
    :param end_sites: Include BVH End Sites in position CSV.
    :type end_sites: bool
    :return: If the write process was successful or not.
    :rtype: bool
    """
    time_col = np.arange(0, (bvh_tree.nframes - 0.5) * bvh_tree.frame_time, bvh_tree.frame_time)[:, None]
    data_list = [time_col]
    header = ['time']
    root = next(bvh_tree.root.filter('ROOT'))
    
    def get_world_positions(joint):
        if joint.value[0] == 'End':
            joint.world_transforms = np.tile(t3d.affines.compose(np.zeros(3), np.eye(3), np.ones(3)),
                                             (bvh_tree.nframes, 1, 1))
        else:
            channels = bvh_tree.joint_channels(joint.name)
            axes_order = ''.join([ch[:1] for ch in channels if ch[1:] == 'rotation']).lower()  # FixMe: This isn't going to work when not all rotation channels are present
            axes_order = 's' + axes_order[::-1]
            joint.world_transforms = get_affines(bvh_tree, joint.name, axes=axes_order)
            
        if joint != root:
            # For joints substitute position for offsets.
            offset = [float(o) for o in joint['OFFSET']]
            joint.world_transforms[:, :3, 3] = offset
            joint.world_transforms = np.matmul(joint.parent.world_transforms, joint.world_transforms)
        if scale != 1.0:
            joint.world_transforms[:, :3, 3] *= scale
            
        header.extend(['{}.{}'.format(joint.name, channel) for channel in 'xyz'])
        pos = joint.world_transforms[:, :3, 3]
        data_list.append(pos)
        
        if end_sites:
            end = list(joint.filter('End'))
            if end:
                get_world_positions(end[0])  # There can be only one End Site per joint.
        for child in joint.filter('JOINT'):
            get_world_positions(child)
    
    get_world_positions(root)
    data = np.concatenate(data_list, axis=1)
    try:
        np.savetxt(filepath, data, header=','.join(header), fmt='%10.5f', delimiter=',', comments='')
        return True
    except IOError as e:
        print("ERROR({}): Could not write to file {}.\n"
              "Make sure you have writing permissions.\n".format(e.errno, filepath))
        return False


def write_joint_hierarchy(bvh_tree, filepath, scale=1.0):
    """Write joints' world positional data to a CSV file.

    :param bvh_tree: BVH tree that holds the data.
    :type bvh_tree: BvhTree
    :param filepath: Destination file path for CSV file.
    :type filepath: str
    :param scale: Scale factor for offset values.
    :type scale: float
    :return: If the write process was successful or not.
    :rtype: bool
    """
    data = list()
    for joint in bvh_tree.get_joints(end_sites=True):
        joint_name = joint.name
        parent_name = bvh_tree.joint_parent(joint_name).name if bvh_tree.joint_parent(joint_name) else ''
        row = [joint_name, parent_name]
        row.extend((scale * offset for offset in bvh_tree.joint_offset(joint.name)))
        data.append(tuple(row))
    data = np.array(data, dtype=[('joint', np.unicode_, 20),
                                 ('parent', np.unicode_, 20),
                                 ('offset.x', np.float),
                                 ('offset.y', np.float),
                                 ('offset.z', np.float)])
    try:
        np.savetxt(filepath,
                   data,
                   header=','.join(data.dtype.names),
                   fmt=['%s', '%s', '%10.5f', '%10.5f', '%10.5f'],
                   delimiter=',',
                   comments='')
        return True
    except IOError as e:
        print("ERROR({}): Could not write to file {}.\n"
              "Make sure you have writing permissions.\n".format(e.errno, filepath))
        return False


@parallelize
def bvh2csv(bvh_path,
            dst_dirpath=None,
            scale=1.0,
            export_rotation=True,
            export_position=True,
            export_hierarchy=True,
            end_sites=True):
    """Converts a BVH file into CSV file format.
    When passing keyword arguments, keywords must be used!

    :param bvh_path: File path(s) for BVH source.
    :type bvh_path: str|list
    :param dst_dirpath: Folder path for destination CSV files.
    :type dst_dirpath: str
    :param scale: Scale factor for root position and offset values.
    :type scale: float
    :param export_rotation: Output rotation CSV file.
    :type export_rotation: bool
    :param export_position: Output world space position CSV file.
    :type export_position: bool
    :param export_hierarchy: Output hierarchy CSV file.
    :type export_hierarchy: bool
    :param end_sites: Include BVH End Sites in position CSV.
    :type end_sites: bool
    :return: If the conversion was successful or not.
    :rtype: bool
    """
    try:
        with open(bvh_path) as file_handle:
            mocap = BvhTree(file_handle.read())
    except IOError as e:
        print("ERROR {}: Could not open file".format(e.errno), bvh_path)
        return False

    # Assume everything works and only set False on error.
    pos_success = True
    rot_success = True
    hierarchy_success = True
    if not dst_dirpath:
        dst_filepath = os.path.join(os.path.dirname(bvh_path), os.path.basename(bvh_path)[:-4])
    else:
        # If the specified path doesn't yet exist, create it.
        if not os.path.exists(dst_dirpath):
            os.mkdir(dst_dirpath)
        dst_filepath = os.path.join(dst_dirpath, os.path.basename(bvh_path)[:-4])
    if export_position:
        pos_success = write_joint_positions(mocap, dst_filepath + '_pos.csv', scale, end_sites)
    if export_rotation:
        rot_success = write_joint_rotations(mocap, dst_filepath + '_rot.csv')
    if export_hierarchy:
        hierarchy_success = write_joint_hierarchy(mocap, dst_filepath + '_hierarchy.csv', scale)

    n_succeeded = sum([pos_success, rot_success, hierarchy_success])
    return bool(n_succeeded)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Convert BVH file to CSV table format.""",
        epilog="""If neither -p nor -r are specified, both CSV files will be created.""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s v{}'.format(get_pkg_version()))
    parser.add_argument("-o", "--out", type=str, default='', help="Destination folder for CSV files.\n"
                                                            "If no destination path is given, BVH file path is used.\n"
                                                            "CSV files will have the source file base name appended by\n"
                                                            "suffixes _rot, _pos, and _hierarchy.csv respectively.")
    parser.add_argument("-s", "--scale", type=float, default=1.0,
                        help="Scale factor for root position and offset values. In case you have to switch from "
                             "centimeters to meters or vice versa.")
    parser.add_argument("-r", "--rotation", action='store_true', help="Output rotation CSV file.")
    parser.add_argument("-p", "--position", action='store_true', help="Output world space position CSV file.")
    parser.add_argument("-e", "--ends", action='store_true', help="Include BVH End Sites in position CSV. "
                                                                  "They do not have rotations.")
    parser.add_argument("-H", "--hierarchy", action='store_true', help="Output skeleton hierarchy to CSV file.")
    parser.add_argument("input.bvh", type=str, help="BVH file path or folder for converting to CSV.")
    args = vars(parser.parse_args(argv))
    src_path = args['input.bvh']
    dst_path = args['out']
    scale = args['scale']
    do_rotation = args['rotation']
    do_position = args['position']
    do_hierarchy = args['hierarchy']
    # If neither rotation nor position are specified, do both.
    if not do_rotation and not do_position:
        do_rotation = True
        do_position = True
    do_end_sites = args['ends']
    
    files = get_bvh_files(src_path)
    success = bvh2csv(files,
                      dst_dirpath=dst_path,
                      scale=scale,
                      export_rotation=do_rotation,
                      export_position=do_position,
                      export_hierarchy=do_hierarchy,
                      end_sites=do_end_sites)
    if not success:
        print("Some errors occurred.")
    return success


if __name__ == "__main__":
    freeze_support()
    exit_code = int(not main())
    sys.exit(exit_code)
