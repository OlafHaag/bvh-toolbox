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

"""Rename joints in BVH files."""

import os
import sys
import argparse
import csv
import re

from .. import get_pkg_version


def rename_joints(source_path, names_map, destination_path=None):
    """Rename joints in a BVH file using a dictionary and save the file.
    
    :param source_path: file path to bvh file.
    :type source_path: str
    :param names_map: Dictionary with old_name: new_name pairs.
    :type names_map: dict
    :param destination_path: Destination file path. If None BVH file is overwritten.
    :type destination_path: str
    :return: Whether writing the changed file was successful or not.
    :rtype: bool
    """
    file_type = os.path.splitext(source_path)[1].lower()
    if file_type != ".bvh":
        print("ERROR: File extension BVH expected for: {}".format(source_path))
        return False

    try:
        with open(source_path, mode='r') as file_handle:
            lines = file_handle.readlines()
    except FileNotFoundError:
        print("ERROR: file {} not found".format(source_path))
        return False

    prog = re.compile("(?<=JOINT|ROOT ).*$")
    
    for idx, line in enumerate(lines):
        if "MOTION\n" in line:
            break
        match = prog.search(line)
        if match:
            joint = match.group().lstrip()
            if joint in names_map:
                lines[idx] = line.replace(joint, names_map[joint])
    
    # If no destination file is specified, overwrite input file.
    if not destination_path:
        destination_path = source_path
    try:
        with open(destination_path, mode='w') as file_handle:
            file_handle.writelines(lines)
    except OSError:
        print("ERROR: Can't write to destination {}".format(destination_path))
        return False
    # If we reached this point, everything went well.
    return True


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Rename joints in BVH files.""",
        epilog="Use Unix-style path separators '/' or double backslash '\\\\' on Windows!\n",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s v{}'.format(get_pkg_version()))
    parser.add_argument("input.bvh", nargs='+', type=str, help="BVH files which joints will be renamed.")
    parser.add_argument("mapping.csv", type=str, help="CSV file containing the mapping of old names to new ones.")
    parser.add_argument("-o", "--out", nargs='*', type=str, help="Destination file paths for BVH files.\n"
                                                                 "If no out path is given, or list is shorter than\n"
                                                                 "input files, BVH files are overwritten.")
    args = vars(parser.parse_args(argv))
    src_files_paths = args['input.bvh']
    dst_files_paths = args['out']
    if not dst_files_paths:
        dst_files_paths = list()
    names_file_path = args['mapping.csv']
    mapping = dict()

    try:
        with open(names_file_path) as file_handle:
            csv_reader = csv.reader(file_handle)
            for row in csv_reader:
                mapping[row[0]] = row[1]
    except OSError as e:
        print("ERROR:", e)
        sys.exit(1)
        
    res = list()
    for i, bvh_file in enumerate(src_files_paths):
        # There could be less destination paths or None.
        if i >= len(dst_files_paths):
            dst_file = None
        else:
            dst_file = dst_files_paths[i]
        res.append(rename_joints(bvh_file, mapping, dst_file))

    num_errors = len(res) - sum(res)
    if num_errors > 0:
        print("ERROR: {} files could not be processed.".format(num_errors))
    return False if num_errors else True


if __name__ == "__main__":
    exit_code = int(not main())
    sys.exit(exit_code)
