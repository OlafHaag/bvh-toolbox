This repository provides *Python3* scripts for manipulating and converting BVH motion capture files.
Following destination formats are supported by the converters:

# BVH to Cal3D XSF & XAF
* Converts BVH files to the [Cal3D](https://github.com/mp3butcher/Cal3D/) XML skeleton (XSF) and animation (XAF) file formats.
* The XAF files rely on the respective skeleton file.
* XAF files have been tested to work with skeletons that were exported from 3DS Max and Blender.
* I use the resulting xaf files in [Worldviz' Vizard](https://www.worldviz.com/vizard), so it's only been tested in this context.

# BVH to Panda3D Egg animation file
* Converts BVH files to the [Panda3D](https://panda3d.org/) animation file egg format.

# BVH to CSV tables
* Converts BVH to comma separated values tables.
* Ouputs one file for joint rotation and one for joint world location.
* Using only the `--rotation` or the `--location` flag you can output only one of the tables.
* The `--out` parameter only takes a directory path as an argument.
* With the `--ends` flag the End Sites are included in the *_loc.csv file.


All converters have a `--scale` parameter taking a float as an argument. You can use it to convert between units for the location and offset values. 

# How to run the converter batch scripts (and circumvent ModuleNotFoundError)
* Open terminal.
* Go to parent directory of the __converters__ folder. Enter, for example:
* `python -m converters.bvh2egg_batch` "*path/to/folder*" [-o "*output/folder*"] [-s 0.01]
* or `python -m converters.bvh2xaf` "*path/to/file.bvh*" [-o "*destination/path/file.xaf*"] [-s 100]
  * Use UNIX style file path separators ( __/__ ) if there are spaces in your path.
  * The statements in square brackets are optional. 
    * `--out` or `-o` Specify the destination of the output. If you don't provide it, files are saved in the source folder.
    * `--scale` or `-s` is a scale factor on the root's translation and joints' offset values in case you need to convert the data to meters or centimeters. This may depend on how you exported the skeleton.
