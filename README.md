This repository provides *Python3* scripts for manipulating and converting BVH motion capture files.
Following destination formats are supported by the converters:

# BVH to Cal3D XSF & XAF
* Converts BVH files to the [Cal3D](https://github.com/mp3butcher/Cal3D/) XML skeleton (XSF) and animation (XAF) file formats.
* The XAF files rely on the respective skeleton file.
* XAF files have been tested to work with skeletons that were exported from 3DS Max and Blender.
* I use the resulting xaf files in [Worldviz' Vizard](https://www.worldviz.com/vizard), so it's only been tested in this context.

# BVH to Panda3D Egg animation file
* Converts BVH files to the [Panda3D](https://panda3d.org/) animation file egg format.

# How to run the converter batch scripts (and circumvent ModuleNotFoundError)
* Open terminal.
* Go to parent directory of the __converters__ folder. Enter, for example:
* `python -m converters.bvh2egg_batch` "*path/to/folder*" [-o "*output/folder*"]
* or `python -m converters.bvh2xaf` "*path/to/file.bvh*" [-o "*destination/path/file.xaf*"]
  * Use UNIX style file path separators ( __/__ ) if there are spaces in your path.
  * The `--out` statement in square brackets is optional. If you don't provide it, files are saved in the source folder.
