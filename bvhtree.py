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

from bvh import Bvh


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
        raise NotImplementedError
