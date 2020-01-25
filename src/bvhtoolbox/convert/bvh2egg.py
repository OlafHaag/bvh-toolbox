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

""" Outputs Panda3D EGG animation files only. No Models!
EGG Syntax: https://www.panda3d.org/manual/index.php?title=Parsing_and_Generating_Egg_Files&oldid=950

<CoordinateSystem> { string }

    This entry indicates the coordinate system used in the egg file; the
    egg loader will automatically make a conversion if necessary.  The
    following strings are valid: Y-up, Z-up, Y-up-right, Z-up-right,
    Y-up-left, or Z-up-left.  (Y-up is the same as Y-up-right, and Z-up
    is the same as Z-up-right.)
    By convention, this entry should only appear at the beginning of the
    file, although it is technically allowed anywhere.  It is an error
    to include more than one coordinate system entry in the same file.
    If it is omitted, Y-up is assumed.

<Comment> { string }
    Optional. Just enter some comment, e.g. the original bvh file name.

<Bundle> name { table-list } <Table> name { table-body }

    A table is a set of animated values for joints.  A tree of tables
    with the same structure as the corresponding tree of joints must be
    defined for each character to be animated.  Such a tree is placed
    under a <Bundle> node, which provides a handle within Panda to the
    tree as a whole.
    Bundles may only contain tables; tables may contain more tables,
    bundles, or any one of the following (<Scalar> entries are optional,
    and default as shown):

<Xfm$Anim> name {
 <Scalar> fps { 24 }
 <Char*> order { sphrt }
 <Scalar> contents { ijkabcphrxyz }
 <V> { values }
}
    This is a table of matrix transforms, one per frame, such as may
    be applied to a joint.  The "contents" string consists of a subset
    of the letters "ijkabcphrxyz", where each letter corresponds to a
    column of the table; <V> is a list of numbers of length(contents)
    * num_frames.  Each letter of the contents string corresponds to a
    type of transformation:
 i, j, k - scale in x, y, z directions, respectively
 a, b, c - shear in xy, xz, and yz planes, respectively
 p, h, r - rotate by pitch, heading, roll
 x, y, z - translate in x, y, z directions
    The net transformation matrix specified by each row of the table
    is defined as the net effect of each of the individual columns'
    transform, according to the corresponding letter in the contents
    string.  The order the transforms are applied is defined by the
    order string:
 s       - all scale and shear transforms
 p, h, r - individual rotate transforms
 t       - all translation transforms

<Xfm$Anim_S$> name {
 <Scalar> fps { 24 }
 <Char*> order { sphrt }
 <S$Anim> i { ... }
 <S$Anim> j { ... }
 ...
}
    This is a variant on the <Xfm$Anim> entry, where each column of
    the table is entered as a separate <S$Anim> table.  This syntax
    reflects an attempt to simplify the description by not requiring
    repetition of values for columns that did not change value during
    an animation sequence.

Example Xfm$Anim_S$:
<CoordinateSystem> { Z-up }
<Table> {
  <Bundle> Armature {
    <Table> "<skeleton>" {
      <Table> hips {
        <Xfm$Anim_S$> xform {
          <Char*> order { sprht }
          <Scalar> fps { 60 }
          <S$Anim> i { <V> { 0.010000 } }  // all frames
          <S$Anim> j { <V> { 0.010000 } }
          <S$Anim> k { <V> { 0.010000 } }
          <S$Anim> p { <V> { 86.126664 83.467179 } }  // frame1 frame2
          <S$Anim> r { <V> { 0.111280 -1.030870 } }
          <S$Anim> h { <V> { 3.826138 -3.703840 } }
          <S$Anim> x { <V> { 0.023575 0.281066 } }
          <S$Anim> y { <V> { -0.499800 -4.718164 } }
          <S$Anim> z { <V> { 0.971407 0.932534 } }
        }
        <Table> left_upper_leg {
          <Xfm$Anim_S$> xform {
            <Char*> order { sprht }
            <Scalar> fps { 60 }
            // Hint: Write only used channels. E.g. only 1 rotation channel for hinge joints.
            <S$Anim> i { <V> { 1.000000 } }  // all frames
            <S$Anim> j { <V> { 1.000000 } }
            <S$Anim> k { <V> { 1.000000 } }
            <S$Anim> x { <V> { -10.781280 } }
            <S$Anim> y { <V> { -3.445208 } }
            <S$Anim> z { <V> { -0.550255 } }
            <S$Anim> p { <V> { 157.939860 -174.182788 } }   // frame1 frame2
            <S$Anim> r { <V> { 2.645316 3.553227 } }
            <S$Anim> h { <V> { 3.881313 1.567402 } }
          }
        }
      }
    }
  }
}

Example Xfm$Anim:
<CoordinateSystem> { Z-up }
<Table> {
  <Bundle> Armature {
    <Table> "<skeleton>" {
      <Table> hips {
        <Xfm$Anim> xform {
          <Char*> order { sprht }
          <Scalar> fps { 60 }
          <Scalar> contents { ijkprhxyz }
          <V> {
            0.010000 0.010000 0.010000 86.126664 0.111280 3.826138 0.023575 -0.499800 0.971407  // frame 1
            0.010000 0.010000 0.010000 83.467179 -1.030870 -3.703840 0.281066 -4.718164 0.932534  // frame 2
          }
        }
        <Table> left_upper_leg {
          <Xfm$Anim> xform {
            <Char*> order { sprht }
            <Scalar> fps { 60 }
            <Scalar> contents { ijkprhxyz }
            <V> {
              1.000000 1.000000 1.000000 157.939860 2.645316 3.881313 -10.781281 -3.445210 -0.550252  // frame 1
              1.000000 1.000000 1.000000 -174.182788 3.553227 1.567402 -10.781279 -3.445206 -0.550260  // frame 2
            }
          }
        }
      }
    }
  }
}
"""

import os
import sys
import re
import argparse
from multiprocessing import freeze_support

import transforms3d as t3d
import numpy as np

from .. import get_pkg_version
from .. import BvhTree
from .. import get_euler_angles, get_affines, prune
from .multiprocess import get_bvh_files, parallelize


def get_joint_data(bvh_tree, joint, scale=1.0):
    """ Extract data for a joint in the BVH tree that is relevant for compiling the egg file content.
    :param bvh_tree: BVH tree that holds the data.
    :type bvh_tree: BvhTree
    :param joint: Joint object to extract data from for egg file.
    :type joint: bvh.BvhNode
    :param scale: Scale factor for root translation and offset values.
    :type scale: float
    :return: egg animation table compatible data
    :rtype: dict
    """
    data = dict()
    # Replace any special characters and spaces in name with underscores.
    data['name'] = re.sub('[^a-zA-Z0-9_]', '_', joint.name)
    data['fps'] = int(round(1.0 / bvh_tree.frame_time))

    # How deep in the tree are we?
    level = 0
    parent = joint.parent
    while parent.value:
        level += 1
        parent = parent.parent
    data['level'] = level
    
    # Is this a leaf node?
    if joint.value[0] == 'End':
        data['leaf'] = True
        offsets = [float(o)*scale for o in joint['OFFSET']]  # Convert to meters or centimeters.
        data['x'] = [offsets[0]]
        data['y'] = [offsets[1]]
        data['z'] = [offsets[2]]
        data['order'] = 'sprht'
        return data  # Stop here for End Sites.
    else:
        data['leaf'] = False
    
    # Or the root joint?
    if not joint.parent.value:
        is_root = True
    else:
        is_root = False

    # Transformation order.
    mapping = {'Xposition': 'x',
               'Yposition': 'y',
               'Zposition': 'z',
               'Xrotation': 'p',
               'Yrotation': 'r',
               'Zrotation': 'h',
               }
    
    channels = bvh_tree.joint_channels(joint.name)  # We could use joint['CHANNELS'][1:], but better to use the getter.
    
    egg_rot_order = ''.join([mapping[ch] for ch in channels if ch[1:] == 'rotation'])  # FixMe: This isn't going to work when not all rotation channels are present
    # Egg format takes the rotation order the other way around.
    egg_rot_order = egg_rot_order[::-1]
    # Full egg transformation order. s is for scale, t for translation.
    data['order'] = 's' + egg_rot_order + 't'
    
    if is_root:
        axes = ''.join([ch[:1] for ch in channels if ch[1:] == 'rotation']).lower()  # FixMe: See above.
        affines = get_affines(bvh_tree, joint.name, axes='r' + axes)
        rotation_offset_aff = t3d.affines.compose(np.zeros(3),
                                                  t3d.euler.euler2mat(*np.radians([90, 0, 0]), axes='sxyz'),
                                                  np.ones(3))
        prune(rotation_offset_aff)
        # Conjugation of affine matrices.
        rotated_affines = np.matmul(rotation_offset_aff, affines)
        # Extract translations and rotations.
        axes = axes[::-1]
        loc_rot = np.array([np.hstack((t, np.degrees(t3d.euler.mat2euler(r, axes='s' + axes)))) for t, r, _, _
                            in map(t3d.affines.decompose44, rotated_affines)])
        eulers = loc_rot[:, 3:]

        rotations = {'p': eulers[:, axes.index('x')],
                     'r': eulers[:, axes.index('y')],
                     'h': eulers[:, axes.index('z')],
                     }
        
        translations = loc_rot[:, :3] * scale
        data['x'] = translations[:, 0]
        data['y'] = translations[:, 1]
        data['z'] = translations[:, 2]
    else:
        euler_xyz = get_euler_angles(bvh_tree, joint.name, axes='xyz')
        
        rotations = {'p': euler_xyz[:, 0],
                     'r': euler_xyz[:, 1],
                     'h': euler_xyz[:, 2],
                     }
        # Write offsets instead of translation for joints.
        offsets = np.array(bvh_tree.joint_offset(joint.name)) * scale
        data['x'] = [offsets[0]]
        data['y'] = [offsets[1]]
        data['z'] = [offsets[2]]
        
    for channel, values in rotations.items():
        unique = np.unique(values)
        if len(unique) == 1:
            data[channel] = unique
        else:
            data[channel] = values

    # Set scale to 1 on all axes.
    data['i'], data['j'], data['k'] = ([1.0],) * 3
    
    return data
    
    
def data2egg(data):
    # How much indentation?
    level = data['level'] + 3  # There are 3 other open tables before the animation tables start.
    
    def anim_table(component):
        table_string = '{0}    <S$Anim> {1} {{ <V> {{ {2} }} }}\n'.format('  ' * level,
                                                                          component,
                                                                          ' '.join(map(str, data[component])))
        return table_string
        
    egg_str  = '{0}<Table> {1} {{\n'.format('  ' * level, data['name'])
    egg_str += '{0}  <Xfm$Anim_S$> xform {{\n'.format('  ' * level)
    egg_str += '{0}    <Char*> order {{ {1} }}\n'.format('  ' * level, data['order'])
    egg_str += '{0}    <Scalar> fps {{ {1} }}\n'.format('  ' * level, data['fps'])
    for comp in 'ijkprhxyz':
        if comp in data.keys():
            egg_str += anim_table(comp)
    
    egg_str += '{0}  }}\n'.format('  ' * level)
    if data['leaf']:
        egg_str += '{0}}}\n'.format('  ' * level)
        
    return egg_str


def close_tables(egg_string, target_level=0):
    """ The egg string is hierarchically ordered. This function appends curly brackets to close open tables.
    It takes the indentation of the last closed bracket as reference for the current level/depth of the hierarchy.
    :param egg_string:
    :type egg_string: str
    :param target_level: The level determinates the target indentation/depth,
    in other words how many tables should be closed.
    :type target_level: int
    :return: egg_string with closed tables.
    :rtype: str
    """
    # Get the last level by counting the spaces to the second to last line break.
    last_level = egg_string[egg_string[:-1].rfind("\n"):].count("  ")
    diff = last_level - target_level
    for level in range(diff):
        egg_string += '{0}}}\n'.format('  ' * (last_level - level - 1))
    return egg_string


def get_egg_anim_tables(bvh_tree, scale=1.0):
    """Get the XML animation tables for the BVH structure as a string.
    
    :param bvh_tree:
    :type bvh_tree: bvh.BVH
    :param scale: Scale factor for root translation and offset values.
    :type scale: float
    :return: string containing the animation tables.
    :rtype: str
    """
    egg_string = ''
    for joint in bvh_tree.get_joints(end_sites=True):
        joint_data = get_joint_data(bvh_tree, joint, scale=scale)
        # Close open tables, before we start a new one with a lesser level.
        egg_string = close_tables(egg_string, joint_data['level'] + 3)
        egg_string += data2egg(joint_data)
    return egg_string


@parallelize
def bvh2egg(bvh_path, dst_path=None, scale=1.0):
    """ Converts a BVH file into the Panda3D egg animation file format.
    When passing keyword arguments, keywords must be used!

    :param bvh_path: File path(s) for BVH source.
    :type bvh_path: str|list
    :param dst_path: File or folder path for destination Panda3D Egg file.
    :type dst_path: str
    :param scale: Scale factor for root translation and offset values.
    :type scale: float
    :return: If the conversion was successful or not.
    :rtype: bool
    """
    with open(bvh_path) as file_handle:
        mocap = BvhTree(file_handle.read())
    
    # Even though the BVH is Y-up, because the skeleton got rotated by 90 degrees around X, Z is now up.
    coords_up = '<CoordinateSystem> { Z-up }\n'
    comment = '<Comment> {{ Converted from {0} }}\n'.format(os.path.basename(bvh_path))
    init_table_str = '<Table> {\n  <Bundle> Armature {\n    <Table> "<skeleton>" {\n'
    
    egg_str = coords_up + comment + init_table_str + get_egg_anim_tables(mocap, scale=scale)
    egg_str = close_tables(egg_str)
    
    if not dst_path:
        dst_path = bvh_path[:-3] + 'egg'
        
    if os.path.isdir(dst_path):
        dst_path = os.path.join(dst_path, os.path.basename(bvh_path)[:-3] + 'egg')
        
    try:
        with open(dst_path, 'w') as file_handle:
            file_handle.write(egg_str)
        return True
    except IOError as e:
        print("ERROR({}): Could not write to file {}.\n"
              "Make sure you have writing permissions.\n".format(e.errno, dst_path))
        return False


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Convert BVH file to Panda3D egg animation (only) file.""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s v{}'.format(get_pkg_version()))
    parser.add_argument("-o", "--out", type=str, help="Destination file for folder path for egg file.\n"
                                                      "If no out path is given, BVH file path is used.")
    parser.add_argument("-s", "--scale", type=float, default=1.0,
                        help="Scale factor for root translation and offset values.\n"
                             "In case you have to switch from centimeters to meters or vice versa.")
    parser.add_argument("input.bvh", type=str, help="BVH source file or folder path to convert to egg.")
    args = vars(parser.parse_args(argv))
    src_path = args['input.bvh']
    dst_path = args['out']
    scale = args['scale']
    
    files = get_bvh_files(src_path)
    success = bvh2egg(files, dst_path=dst_path, scale=scale)
    return success


if __name__ == "__main__":
    freeze_support()
    exit_code = int(not main())
    sys.exit(exit_code)
