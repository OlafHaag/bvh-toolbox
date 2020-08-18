This repository provides *Python3* scripts for manipulating and converting BVH motion capture files.

[![Latest version on PyPI](https://img.shields.io/pypi/v/bvhtoolbox.svg)](https://pypi.org/project/bvhtoolbox)
[![Test Python package](https://github.com/OlafHaag/bvh-toolbox/workflows/Test%20Python%20package/badge.svg)](https://github.com/OlafHaag/bvh-toolbox/actions?query=workflow%3A%22Test+Python+package%22)

# Installation
* To install from PyPi:  
`pip install bvhtoolbox`
* To install from github using development mode:  
`pip install -e git+https://github.com/OlafHaag/bvh-toolbox.git@master#egg=bvhtoolbox`
* To install latest development version using regular mode (building the package):  
`pip install https://github.com/OlafHaag/bvh-toolbox/archive/master.zip`
* The installation creates some console scripts you can use.

# Console scripts
## Manipulate BVH files
### Rename joints in bvh files
* Command: **bvhrenamejoints**

### Remove frames from BVH files
* Command: **bvhremoveframes**

### Offset joint angles in BVH files
* Command: **bvhoffsetjointangles**
* Can be used to additively offset joint angles in the BVH by supplying a csv table containing the mapping of joint names to euler angles.
  * The angles must be in the same order as the joint's channels in the BVH hierarchy.

## Convert from or to BVH files

### BVH to Cal3D XSF & XAF
* Command: **bvh2xsf**
* Command: **bvh2xaf**
* Converts BVH files to the [Cal3D](https://github.com/mp3butcher/Cal3D/) XML skeleton (XSF) and animation (XAF) file formats.
* The XAF files rely on the respective skeleton file.
* XAF files have been tested to work with skeletons that were exported from 3DS Max and Blender.
* I use the resulting xaf files in [Worldviz' Vizard](https://www.worldviz.com/vizard), so it's only been tested in this context.

### BVH to Panda3D Egg animation file
* Command: **bvh2egg**
* Converts BVH files to the [Panda3D](https://panda3d.org/) animation file egg format.

### BVH to CSV tables
* Command: **bvh2csv**
* Converts BVH to comma separated values tables.
* Ouputs one file for hierarchy, one for joint rotations, and one for joint world positions.
* Use `--hierarchy` to export the respective CSV file.
* Using only the `--rotation` or the `--position` flag you can output only one of the transform tables.
* The `--out` parameter only takes a directory path as an argument.
* With the `--ends` flag the End Sites are included in the *_pos.csv file.

### CSV tables to BVH
* Command: **csv2bvh**
* Takes 3 CSV files (hierarchy, rotation, position) previously exported using *bvh2csv* or created otherwise and builds a bvh file from them.

All converters have a `--scale` parameter taking a float as an argument. You can use it to convert between units for the position and offset values.

# How to run the console batch scripts
* Open terminal.
* If you've installed the bvhtoolbox into a conda/virtual environment, you have to activate it first.
* type `<script_name> -h` (substitute *<script_name>* by one of the commands above) to get more information on the usage.

# Notes
This package includes 20tabs' bvh module due to a lack of updates for this module on pypi.org.
