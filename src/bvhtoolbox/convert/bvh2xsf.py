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

""" Convert BVH files to Cal3d XSF Skeleton format.
Sets bones to zero rotation as BVH format doesn't support joint rotations in hierarchy.
That means every joint in a BVH is setup to be aligned with the world space, which is not very animator friendly.
So a mesh file must be exported on such a skeleton (e.g. T-Pose) to be compatible with skeletons exported by this script.

XSF Syntax:
Joint names have BoneIDs assigned in the Cal3d skeleton file.
<SKELETON MAGIC="XSF" VERSION="1000" NUMBONES="3">
    <BONE ID="0" NAME="root" NUMCHILDS="1">
        <TRANSLATION>0 0 0</TRANSLATION>
        <ROTATION>-0.707107 0 0 0.707107</ROTATION>
        <LOCALTRANSLATION>-0 -0 -0</LOCALTRANSLATION>
        <LOCALROTATION>0.707107 0 0 0.707107</LOCALROTATION>
        <PARENTID>-1</PARENTID>
        <CHILDID>1</CHILDID>
    </BONE>
    <BONE ID="1" NAME="middle" NUMCHILDS="1">
        <TRANSLATION>0 0.5 5.1658e-08</TRANSLATION>
        <ROTATION>0 -5.96046e-08 -8.88179e-16 1</ROTATION>
        <LOCALTRANSLATION>4.38176e-15 -0.5 -5.1658e-08</LOCALTRANSLATION>
        <LOCALROTATION>0.707107 4.21468e-08 4.21468e-08 0.707107</LOCALROTATION>
        <PARENTID>0</PARENTID>
        <CHILDID>2</CHILDID>
    </BONE>
</SKELETON>

Rotations are stored relative to parent joint as quaternions (xyzw).
https://github.com/imvu/cal3d/blob/master/tools/converter/fileformats.txt
"""

import os
import argparse
import sys
import xml.etree.ElementTree as XmlTree
import itertools

import numpy as np
import transforms3d as t3d

from .. import get_pkg_version
from .. import BvhTree
from .prettify_elementtree import prettify


def get_bone_xml(bvh_tree, joint_name, scale=1.0):
    """Build the XML structure for a joints topological data.
    
    :param bvh_tree: BVH tree that holds the data.
    :type bvh_tree: BvhTree
    :param joint_name: Name of joint to extract data from for egg file.
    :type joint_name: str
    :param scale: Scale factor for root translation and offset values.
    :type scale: float
    :return: XML structure with topological data for this joint.
    :rtype: xml.etree.ElementTree.Element
    """
    # Get direct child joints.
    children = bvh_tree.joint_children(joint_name)
    
    bone_xml = XmlTree.Element('BONE', {'ID': str(bvh_tree.get_joint_index(joint_name)),
                                        'NAME': joint_name,
                                        'NUMCHILDS': str(len(children)),
                                        })
    
    offsets = [float(o) * scale for o in bvh_tree.joint_offset(joint_name)]  # Convert to meters.
    world_trans = t3d.affines.compose(offsets, np.identity(3), np.ones(3))
    parent_id = bvh_tree.joint_parent_index(joint_name)
    if parent_id:
        rot_str = "0 0 0 1"  # Quaternion (x, y, z, w)
    else:
        rot_str = np.array_str(np.roll(t3d.euler.euler2quat(*np.radians([-90., 0., 0.])), -1))[1:-1]
        offsets[1:] = offsets[-1:-3:-1]  # Switch Y and Z because the root is rotated around the X-Axis by -90 degrees.
    offsets_str = '{} {} {}'.format(offsets[0], offsets[1], offsets[2])
    # All joints get rotated by 90 degrees.
    loc_rot = np.roll(t3d.euler.euler2quat(*np.radians([90., -0., 0.])), -1)
    loc_rot_str = str(loc_rot)[1:-1]
    
    # Construct world position of joint.
    parent = bvh_tree.joint_parent(joint_name)
    while parent:
        parent_offsets = [float(o) * scale for o in bvh_tree.joint_offset(parent.name)]
        parent_trans = t3d.affines.compose(parent_offsets, np.identity(3), np.ones(3))
        world_trans = np.matmul(world_trans, parent_trans)
        parent = bvh_tree.joint_parent(parent.name)
    t_world = world_trans[:3, -1]
    
    XmlTree.SubElement(bone_xml, "TRANSLATION").text = offsets_str
    XmlTree.SubElement(bone_xml, "ROTATION").text = rot_str
    XmlTree.SubElement(bone_xml, "LOCALTRANSLATION").text = str(-t_world)[1:-1]
    XmlTree.SubElement(bone_xml, "LOCALROTATION").text = loc_rot_str
    XmlTree.SubElement(bone_xml, "PARENTID").text = str(parent_id)
    
    for child in children:
        XmlTree.SubElement(bone_xml, "CHILDID").text = str(bvh_tree.get_joint_index(child.name))
        
    return bone_xml
    
    
def bvh2xsf(bvh_filepath, dst_filepath=None, scale=1.0):
    """Converts a BVH file into the Cal3D XSF skeleton file format.

    :param bvh_filepath: File path for BVH source.
    :type bvh_filepath: str
    :param dst_filepath: File path for destination Cal3D skeleton file (XSF).
    :type dst_filepath: str
    :param scale: Scale factor for root translation and offset values.
    :type scale: float
    """
    try:
        with open(bvh_filepath) as file_handle:
            mocap = BvhTree(file_handle.read())
    except OSError as e:
        print("ERROR:", e)
        return False

    joints = mocap.get_joints_names(end_sites=True)
    
    xml_root = XmlTree.Element("SKELETON")
    xml_root.set('MAGIC', 'XSF')
    xml_root.set('VERSION', '1100')
    xml_root.set('NUMBONES', str(len(joints)))
    comment = XmlTree.Comment('Converted from {}'.format(os.path.basename(bvh_filepath)))
    xml_root.append(comment)
    # Use map to compute tracks.
    bones = list(map(get_bone_xml, itertools.repeat(mocap), joints, itertools.repeat(scale)))
    # Extend tracks to xml_root as children.
    xml_root.extend(bones)
    # Add indentation.
    xml_str = prettify(xml_root)

    if not dst_filepath:
        dst_filepath = bvh_filepath[:-3] + 'xsf'
    try:
        with open(dst_filepath, 'w') as file_handle:
            file_handle.write(xml_str)
    except IOError as e:
        print("ERROR({}): Could not write to file {}.\n"
              "Make sure you have writing permissions.\n".format(e.errno, dst_filepath))
        return False
    return True


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Convert BVH file to Cal3D ASCII skeleton file (XSF).""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s v{}'.format(get_pkg_version()))
    parser.add_argument("-o", "--out", type=str, help="Destination file path for XSF file.\n"
                                                      "If no out path is given, BVH file path is used.")
    parser.add_argument("-s", "--scale", type=float, default=1.0,
                        help="Scale factor for root translation and offset values.\n"
                             "In case you have to switch from centimeters to meters or vice versa.")
    parser.add_argument("input.bvh", type=str, help="BVH source file to convert to XSF.")
    args = vars(parser.parse_args(argv))
    src_file_path = args['input.bvh']
    dst_file_path = args['out']
    scale = args['scale']
    
    success = bvh2xsf(src_file_path, dst_file_path, scale)
    return success
    
    
if __name__ == "__main__":
    exit_code = int(not main())
    sys.exit(exit_code)
