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

from . import Bvh


class BvhTree(Bvh, object):  # Bvh is an old-style class, so we need object to fix super() in Python 2.x.
    """Extend the Bvh class with functions including End Sites and writing to file."""

    def __init__(self, data):
        super(BvhTree, self).__init__(data)
        # Rename End Sites.
        end_sites = self.search('End')
        for end in end_sites:
            end.value[1] = end.parent.name + "_End"
    
    def get_joints_names(self, end_sites=False):
        """
        :param end_sites: Whether to include End Sites.
        :type end_sites: bool
        :return: List of joint names as strings.
        :rtype: list
        """
        joints = []
    
        def iterate_joints(joint):
            joints.append(joint.value[1])
            if end_sites:
                end = list(joint.filter('End'))
                if end:
                    joints.append(end[0].value[1])  # There can be only one End Site per joint.
            for child in joint.filter('JOINT'):
                iterate_joints(child)
    
        iterate_joints(next(self.root.filter('ROOT')))
        return joints

    def get_joints(self, end_sites=False):
        """
        :param end_sites: Whether to include End Sites.
        :type end_sites: bool
        :return: List of joints as BvhNodes.
        :rtype: list
        """
        joints = []

        def iterate_joints(joint):
            joints.append(joint)
            if end_sites:
                end = list(joint.filter('End'))
                if end:
                    joints.append(end[0])  # There can be only one End Site per joint.
            for child in joint.filter('JOINT'):
                iterate_joints(child)
                
        iterate_joints(next(self.root.filter('ROOT')))
        return joints
    
    def get_joint(self, name):
        found = self.search('ROOT', name)
        if not found:
            found = self.search('JOINT', name)
        if not found:
            found = self.search('End', name)
        if found:
            return found[0]
        raise LookupError('joint not found')
    
    def get_joint_index(self, name):
        return self.get_joints(end_sites=True).index(self.get_joint(name))
    
    def joint_children(self, name):
        """Return direct child joints or End Site."""
        joint = self.get_joint(name)
        children = list()
        for child in joint.filter('JOINT'):
            children.append(child)
        for child in joint.filter('End'):  # There's maximum 1 End Site as child.
            children.append(child)
        return children
        
    def write_file(self, file_path):
        """
        :param file_path: Destination path for BVH file.
        :type file_path: str
        :return: If writing to file was possible.
        :rtype: bool
        """
        try:
            with open(file_path, "w") as file_handle:
                self.write(file_handle)
            return True
        except OSError as e:
            print("ERROR:", e)
            return False
            
    def write(self, out_stream):
        out_stream.write(self._get_hierarchy_string())
        out_stream.write(self._get_motion_string())

    def _get_hierarchy_string(self):
        s = 'HIERARCHY\n'
        for joint in self.get_joints(end_sites=True):
            s = self._close_scopes(s, self.get_joint_depth(joint.name))
            s += self._get_joint_string(joint)
        s = self._close_scopes(s)
        return s

    def get_joint_depth(self, name):
        # How deep in the tree are we?
        depth = 0
        parent = self.joint_parent(name)
        while parent:
            depth += 1
            parent = self.joint_parent(parent.name)
        return depth
        
    def _get_joint_string(self, joint):
        depth = self.get_joint_depth(joint.name)
        
        if not self.joint_children(joint.name):
            s = '{0}{1}\n'.format('  ' * depth, 'End Site')
            s += '{0}{{\n'.format('  ' * depth)
            s += '{0}{1} {2}\n'.format('  ' * (depth+1), 'OFFSET', ' '.join(joint['OFFSET']))
            s += '{0}}}\n'.format('  ' * depth)
        else:
            s = '{0}{1}\n'.format('  ' * depth, str(joint))
            s += '{0}{{\n'.format('  ' * depth)
            for attribute in ['OFFSET', 'CHANNELS']:
                s += '{0}{1} {2}\n'.format('  ' * (depth + 1), attribute, ' '.join(joint[attribute]))
        return s
    
    def _close_scopes(self, hierarchy_string, target_depth=0):
        """ The string is hierarchically ordered. This function appends curly brackets to close open scopes.
        It takes the indentation of the last closed bracket as reference for the current level/depth of the hierarchy.
        :param hierarchy_string:
        :type hierarchy_string: str
        :param target_depth: The depth determines the target indentation.
        :type target_depth: int
        :return: string with closed scopes.
        :rtype: str
        """
        # Get the last level by counting the spaces to the second to last line break.
        last_depth = hierarchy_string[hierarchy_string[:-1].rfind("\n"):].count("  ")
        diff = last_depth - target_depth
        for depth in range(diff):
            hierarchy_string += '{0}}}\n'.format('  ' * (last_depth - depth - 1))
        return hierarchy_string

    def _get_motion_string(self):
        s = 'MOTION\n'
        s += 'Frames: {}\n'.format(self.nframes)
        s += 'Frame Time: {}\n'.format(self.frame_time)
        for frame in self.frames:
            s += ' '.join(frame)
            s += '\n'
        return s
