import glob
import os
import sys
from functools import wraps, partial
from multiprocessing import Pool, cpu_count
from pickle import PicklingError
import time


def parallelize(fn, *args):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        # Keep track of when we started.
        t0 = time.time()
        
        # Check if the first argument are multiple files.
        if isinstance(args[0], (list, tuple)):
            n_files = len(args[0])
            print("Converting {} file{}...".format(n_files, "s" if n_files != 1 else ""))

            if n_files == 0:
                print("WARNING: No BVH files to convert.")
                return False
            elif n_files == 1:
                success = fn(args[0][0], **kwargs)
            else:
                cpus = cpu_count()
                n_processes = min(n_files, cpus)
                partial_func = partial(fn, **kwargs)
                try:
                    print("\nCreating pool with {} processes.".format(n_processes))
                    with Pool(processes=n_processes) as p:
                        results = p.map(partial_func, args[0])  # FixMe: Can't pickle.
                except PicklingError:
                    print("WARNING: Known issue encountered with multiprocessing.\n"
                          "Switching to sequential processing.")
                    #results = list(map(partial_func, args[0]))
                    # More verbose feedback.
                    results = []
                    for i, file in enumerate(args[0]):
                        print("Converting file {}/{}: {}".format(i+1, len(args[0]), file))
                        results.append(fn(file, **kwargs))
                    
                # Were there errors?
                num_errors = len(results) - sum(results)
                if num_errors:
                    print("ERROR: {} conversions were not successful.".format(num_errors))
                success = not num_errors
        else:  # Assume the first argument is a single file path.
            print("Converting 1 file...")
            success = fn(args[0], **kwargs)

        print("Processing took: {:.2f} seconds".format(time.time() - t0))
        return success

    # Trying to fix PicklingError.
    #wrapped.__module__ = "__main__"  # For Python 2 only? Todo: Test in Python 2
    #setattr(sys.modules[fn.__module__], fn.__name__, wrapped)  # Not working either.
    
    return wrapped


def get_bvh_files(in_path):
    if not os.path.exists(in_path):
        print("ERROR: {} does not exist.".format(in_path))
        return []
    
    if os.path.isdir(in_path):
        os.chdir(in_path)
        # Collect all BVH files in folder and pair with out file as arguments for converter.
        file_names = glob.glob("*.bvh")
        return file_names
    else:
        return in_path
