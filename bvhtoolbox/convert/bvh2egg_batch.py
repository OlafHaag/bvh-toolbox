import os
import sys
import argparse
from multiprocessing import Pool, freeze_support
import time
import glob

from bvhtoolbox.convert import bvh2egg


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Convert BVH files to Panda3D egg animation (only) files.""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s 0.1')
    parser.add_argument("-o", "--out", type=str, help="Destination folder path for egg files.\n"
                                                      "If no out path is given, BVH folder is used.")
    parser.add_argument("-s", "--scale", type=float, default=1.0,
                        help="Scale factor for root translation and offset values.\n"
                             "In case you have to switch from centimeters to meters or vice versa.")
    parser.add_argument("input folder", type=str, help="Folder containing BVH source files.")
    args = vars(parser.parse_args(argv))
    src_folder_path = args['input folder']
    dst_folder_path = args['out']
    scale = args['scale']
    if not dst_folder_path:
        dst_folder_path = ''
        
    if not os.path.exists(src_folder_path):
        print("ERROR: Folder not found", src_folder_path)
        sys.exit(1)
    
    os.chdir(src_folder_path)
    # Keep track of when we started.
    t0 = time.time()
    # Collect all BVH files in folder and pair with out file as arguments for converter.
    file_args = list()
    for filename in glob.glob("*.bvh"):
        file_args.append((filename, os.path.join(dst_folder_path, filename[:-3] + 'egg'), scale))
    
    print("Converting {} files...".format(len(file_args)))
    n_processes = min(len(file_args), 8)
    print("\nCreating pool with {} processes".format(n_processes))
    with Pool(processes=n_processes) as p:
        res = p.starmap(bvh2egg, file_args)
    print("Processing took: {:.2f} seconds".format(time.time()-t0))
    # Were there errors?
    num_errors = len(res) - sum(res)
    if num_errors > 0:
        print("ERROR: {} files could not be processed.".format(num_errors))
    return False if num_errors else True


if __name__ == "__main__":
    freeze_support()
    exit_code = int(not main())
    sys.exit(exit_code)
