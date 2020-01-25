import argparse
import os
import sys

from .. import get_pkg_version


def remove_frames(file_path, start, end=None, dst_file=None):
    """Delete frames in BVH file from start to end or to the end of file.

    :param file_path: BVH file to delete frames from.
    :type file_path: str
    :param start: First frame to be deleted. Frame count starts with 1.
    :type start: int
    :param end: Last frame to be deleted. If None, all frames after start are removed.
    :type end: int
    :param dst_file: If you want to save to a new file, specify its path.
    :type dst_file: str
    :return: Whether the file could be processed and saved.
    :rtype: bool
    """
    # Sanity Check on start and end.
    if end and (start >= end):
        print("First frame to remove is greater than last frame to remove. Aborting.\n"
              "File: {]".format(file_path))
        return False

    file_type = os.path.splitext(file_path)[1].lower()
    if file_type != ".bvh":
        print("ERROR: File extension BVH expected for: {}".format(file_path))
        return False

    try:
        with open(file_path, mode='r') as file_handle:
            lines = file_handle.readlines()
    except FileNotFoundError:
        print("ERROR: file {} not found".format(file_path))
        return False

    # Find first frame.
    frames_idx = lines.index(next(line for line in lines if line.startswith('Frames:')))
    frame1_idx = frames_idx + 2

    # Slice together the parts we want to keep.
    if end:
        lines = lines[:start + frame1_idx - 1] + lines[end + frame1_idx:]
    else:
        lines = lines[:start + frame1_idx - 1]

    # We need to update Frames:
    num_frames = len(lines[frame1_idx:])
    lines[frames_idx] = "Frames: {}\n".format(num_frames)

    # If no destination file is specified, overwrite input file.
    if not dst_file:
        dst_file = file_path
    try:
        with open(dst_file, mode='w') as file_handle:
            file_handle.writelines(lines)
    except OSError:
        print("ERROR: Can't write to destination {}".format(dst_file))
        return False
    # If we reached this point, everything went well.
    return True


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Delete range of frames from BVH files.""",
        epilog="Use Unix-style path separators '/' or double backslash '\\\\' on Windows!\n",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s v{}'.format(get_pkg_version()))
    parser.add_argument("input.bvh", nargs='+', type=str, help="BVH files to remove frames from.")
    parser.add_argument("start", type=int, help="The first frame you want to remove. Count begins at 1.")
    parser.add_argument("-e", "--end", type=int, help="The last frame you want to remove.")
    parser.add_argument("-o", "--out", nargs='*', type=str, help="Destination file paths for BVH files.\n"
                                                                 "If no out path is given, or list is shorter than\n"
                                                                 "input files, BVH files are overwritten.")
    args = vars(parser.parse_args(argv))
    src_files_paths = args['input.bvh']
    dst_files_paths = args['out']
    if not dst_files_paths:
        dst_files_paths = list()
    start = args['start']
    end = args['end']

    res = list()
    for i, bvh_file in enumerate(src_files_paths):
        # There could be less destination paths or None.
        if i >= len(dst_files_paths):
            dst_file = None
        else:
            dst_file = dst_files_paths[i]
        res.append(remove_frames(bvh_file, start, end, dst_file))

    num_errors = len(res) - sum(res)
    if num_errors > 0:
        print("ERROR: {} files could not be processed.".format(num_errors))
    return False if num_errors else True


if __name__ == "__main__":
    exit_code = int(not main())
    sys.exit(exit_code)
