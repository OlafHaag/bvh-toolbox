import os
import sys
import argparse
from multiprocessing import Pool, freeze_support
import time
import glob

from converters.bvh2egg import bvh2egg

if __name__ == "__main__":
    freeze_support()
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="""Convert BVH files to Panda3D egg animation (only) files.""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-v", "--ver", action='version', version='%(prog)s 0.1')
    parser.add_argument("-o", "--out", type=str, help="Destination folder path for egg files. "
                                                      "If no out path is given, BVH folder is used.")
    parser.add_argument("-s", "--scale", type=float, default=1.0,
                        help="Scale factor for root translation and offset values. In case you have to switch from "
                             "centimeters to meters or vice versa.")
    parser.add_argument("input folder", type=str, help="Folder containing BVH source files.")
    args = vars(parser.parse_args())
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
    PROCESSES = min(len(file_args), 8)
    print("\nCreating pool with {} processes".format(PROCESSES))
    with Pool(processes=PROCESSES) as p:
        res = p.starmap(bvh2egg, file_args)
    print("Processing took: {:.2f} seconds".format(time.time()-t0))
    # Were there errors?
    if sum(res) != len(res):
        print("ERROR: Not all conversions were successful.")
