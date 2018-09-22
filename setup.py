#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='bvhtoolbox',
      version='0.1a2',
      description='Python module for reading, manipulating and converting BVH mocap files',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Olaf Haag',
      author_email='haag.olaf@gmail.com',
      url='https://github.com/olafhaag/bvh-toolbox',
      classifiers=[
        'License :: OSI Approved :: MIT License',
        #'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
      ],
      keywords='bvh BioVision mocap convert animation 3d',
      packages=find_packages(exclude=['convert/example_files']),
      install_requires=['bvh > 0.3',  # You may have to get version >0.3 from https://github.com/20tab/bvh-python.
                        'numpy',  # >= 1.15
                        'transforms3d >= 0.3.1'],
      extras_require={'dev': ['sympy', 'panda3d'],
                      },
      entry_points={'console_scripts': ['bvh2csv=convert/bvh2csv_batch:main',
                                        'bvh2egg=convert/bvh2egg_batch:main',
                                        'bvh2xaf=convert/bvh2xaf_batch:main',
                                        'bvh2xsf=convert/bvh2xsf:main',
                                        'bvhoffsetjointangles=manipulate/offsetjointangles:main',
                                        'bvhremoveframes=manipulate/removeframes:main'
                                        'bvhrenamejoints=manipulate/renamejoints:main'
                                        ],
                    },
      project_urls={'Bug Reports': 'https://github.com/olafhaag/bvh-toolbox/issues',
                    'Source': 'https://github.com/olafhaag/bvh-toolbox/',
                    },
      )
