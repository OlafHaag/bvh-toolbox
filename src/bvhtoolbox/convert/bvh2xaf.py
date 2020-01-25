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

""" Convert BVH files to Cal3d XAF Animation format.
The animations work on an exported skeleton from 3DS Max/Blender or from bvh2xsf.py.
These programs have right handed coordinate systems with Z-up.
Vizard seems to use left handed coordinate system with Y-up.

XAF Syntax:
<ANIMATION MAGIC="XAF" VERSION="1100" DURATION="3.33333" NUMTRACKS="24">
    <TRACK BONEID="0" NUMKEYFRAMES="201">
        <KEYFRAME TIME="0">
            <TRANSLATION>0.0235751 -0.499799 0.971407</TRANSLATION>
            <ROTATION>-0.682402 -0.0235033 -0.023727 0.730214</ROTATION>
        </KEYFRAME>
        <KEYFRAME TIME="0.0166667">
            <TRANSLATION>0.0235751 -0.499799 0.971407</TRANSLATION>
            <ROTATION>-0.682402 -0.0235033 -0.023727 0.730214</ROTATION>
        </KEYFRAME>
        ...
        ...
    </TRACK>
    <TRACK BONEID="23" NUMKEYFRAMES="201">
        <KEYFRAME TIME="0">
            <TRANSLATION>0.15 7.62939e-08 0</TRANSLATION>
            <ROTATION>-2.23517e-08 7.45058e-09 -1.49012e-08 1</ROTATION>
        </KEYFRAME>
        <KEYFRAME TIME="0.0166667">
            <TRANSLATION>0.15 7.62939e-08 0</TRANSLATION>
            <ROTATION>-2.23517e-08 7.45058e-09 -1.49012e-08 1</ROTATION>
        </KEYFRAME>
        ...
        ...
    </TRACK>
</ANIMATION>

Joint names have BoneIDs assigned in the Cal3d skeleton file.
<SKELETON VERSION="1000" NUMBONES="24">
    <BONE ID="0" NAME="pelvis" NUMCHILDS="3">
        <TRANSLATION>0.0235751 -0.499799 0.971407</TRANSLATION>
        <ROTATION>-0.682402 -0.0235033 -0.023727 0.730214</ROTATION>
        <LOCALTRANSLATION>0.0117153 -0.935375 -0.564734</LOCALTRANSLATION>
        <LOCALROTATION>0.682402 0.0235033 0.023727 0.730214</LOCALROTATION>
        <PARENTID>-1</PARENTID>
        <CHILDID>1</CHILDID>
        <CHILDID>5</CHILDID>
        <CHILDID>9</CHILDID>
    </BONE>
    
BoneIDs are assigned to joints following the order in the BVH file (depth-first).
Rotations are stored relative to parent joint as quaternions.
https://github.com/imvu/cal3d/blob/master/tools/converter/fileformats.txt
"""

import os
import sys
import argparse
import xml.etree.ElementTree as XmlTree
import itertools
from multiprocessing import freeze_support

import numpy as np
import transforms3d as t3d

from .. import get_pkg_version
from .. import BvhTree
from .. import get_quaternions, get_translations
from .prettify_elementtree import prettify
from .multiprocess import get_bvh_files, parallelize


def get_track(bvh_tree, joint_name, scale=1.0):
    """Build the XML structure for a joints animation data.
    
    :param bvh_tree: BVH tree that holds the data.
    :type bvh_tree: BvhTree
    :param joint_name: Name of joint to extract data from.
    :type joint_name: str
    :param scale: Scale factor for root translation and offset values.
    :type scale: float
    :return: XML structure with animation data for this joint.
    :rtype: xml.etree.ElementTree.Element
    """
    n_frames = bvh_tree.nframes
    # Find correct BoneID (when End Sites are included).
    track = XmlTree.Element("TRACK", {'BONEID': str(bvh_tree.get_joint_index(joint_name)),
                                      'NUMKEYFRAMES': str(n_frames)
                                      })
    
    # Transform into left handed coordinate system with Y still as up-axis.
    """
    # Wiki: Like rotation matrices, quaternions must sometimes be renormalized due to rounding errors,
    # to make sure that they correspond to valid rotations. The computational cost of renormalizing a
    # quaternion, however, is much less than for normalizing a 3 × 3 matrix.
    """
    quats = get_quaternions(bvh_tree, joint_name, axes='rzxy')
    if not bvh_tree.joint_parent(joint_name):
        is_root = True
        # The root in the skeleton definition gets rotated by -90 degrees around X. Do the same here.
        quat_offset = t3d.euler.euler2quat(*np.radians([-90, 0, 0]), axes='sxyz')
        quats = np.array(list(map(t3d.quaternions.qmult, quats, itertools.repeat(quat_offset))))
        # For whatever reason switch w and x.
        quats[:, 0], quats[:, 1] = quats[:, 1], quats[:, 0].copy()
        # Root translation.
        translations = get_translations(bvh_tree, joint_name) * scale
        # Invert Z direction.
        translations[:, 2] *= -1
        # Because of the rotation, we need to switch Y and Z translation.
        translations[:, 1], translations[:, 2] = translations[:, 2], translations[:, 1].copy()
    else:
        is_root = False
        # Invert the xyz-vector.
        quats[:, 1:] *= -1
    # Cal3D needs the quaternions in x, y, z, w.
    quats = np.roll(quats, shift=-1, axis=1)
    
    offsets = bvh_tree.joint_offset(joint_name)
    offsets_str = '{} {} {}'.format(offsets[0]*scale, offsets[1]*scale, offsets[2]*scale)
    # For non-root joints use offset.
    t_str = offsets_str
    
    def get_keyframe(frame):
        nonlocal t_str
        time = frame * bvh_tree.frame_time
        keyframe = XmlTree.Element("KEYFRAME", {'TIME': str(time)})
    
        # Only root should have translation.
        if is_root:
            t = translations[frame]
            # Convert to string for xml. Exclude square brackets at beginning and end. Slicing way faster than re.sub.
            t_str = str(t)[1:-1]
        
        r = quats[frame]
        # Convert to string for xml. Exclude square brackets.
        r_str = np.array2string(r, precision=8, floatmode='maxprec', suppress_small=True)[1:-1]
        
        XmlTree.SubElement(keyframe, "TRANSLATION").text = t_str
        XmlTree.SubElement(keyframe, "ROTATION").text = r_str
        return keyframe
    
    keyframes = list(map(get_keyframe, list(range(n_frames))))
    track.extend(keyframes)
    
    return track


@parallelize
def bvh2xaf(bvh_path, dst_path=None, scale=1.0):
    """ Converts a BVH file into the Cal3D XAF animation file format.
    When passing keyword arguments, keywords must be used!

    :param bvh_path: File path(s) for BVH source.
    :type bvh_path: str|list
    :param dst_path: File or folder path for destination Cal3D animation file (XAF).
    :type dst_path: str
    :param scale: Scale factor for root translation and offset values.
    :type scale: float
    :return: If the conversion was successful or not.
    :rtype: bool
    """
    with open(bvh_path) as file_handle:
        mocap = BvhTree(file_handle.read())
    
    duration = (mocap.nframes - 1) * mocap.frame_time
    joint_names = mocap.get_joints_names()
    n_tracks = len(joint_names)
    
    xml_root = XmlTree.Element("ANIMATION")
    xml_root.set('VERSION', '1100')
    xml_root.set('MAGIC', 'XAF')
    xml_root.set('DURATION', str(duration))
    xml_root.set('NUMTRACKS', str(n_tracks))
    comment = XmlTree.Comment('Converted from {}'.format(os.path.basename(bvh_path)))
    xml_root.append(comment)
    # Use map to compute tracks.
    tracks = list(map(get_track, itertools.repeat(mocap), joint_names, itertools.repeat(scale)))
    # Extend tracks to xml_root as children.
    xml_root.extend(tracks)
    # Add indentation.
    xml_str = prettify(xml_root)
    
    if not dst_path:
        dst_path = bvh_path[:-3] + 'xaf'
        
    if os.path.isdir(dst_path):
        dst_path = os.path.join(dst_path, os.path.basename(bvh_path)[:-3] + 'xaf')
        
    try:
        with open(dst_path, 'w') as file_handle:
            file_handle.write(xml_str)
        return True
    except IOError as e:
        print("ERROR({}): Could not write to file {}.\n"
              "Make sure you have writing permissions.\n".format(e.errno, dst_path))
        return False
        

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Convert BVH file to Cal3D XAF animation file.""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s v{}'.format(get_pkg_version()))
    parser.add_argument("-o", "--out", type=str, help="Destination file for folder path for XAF file.\n"
                                                      "If no out path is given, BVH file path is used.")
    parser.add_argument("-s", "--scale", type=float, default=1.0,
                        help="Scale factor for root translation and offset values.\n"
                             "In case you have to switch from centimeters to meters or vice versa.")
    parser.add_argument("input.bvh", type=str, help="BVH source file or folder path to convert to XAF.")
    args = vars(parser.parse_args(argv))
    src_path = args['input.bvh']
    dst_path = args['out']
    scale = args['scale']
    
    files = get_bvh_files(src_path)
    success = bvh2xaf(files, dst_path=dst_path, scale=scale)
    return success


if __name__ == "__main__":
    freeze_support()
    exit_code = int(not main())
    sys.exit(exit_code)
