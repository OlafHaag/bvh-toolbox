#!/usr/bin/env python
""" Installation script for bvhtoolbox package """

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
      version='0.1.2',
      description='Python module for reading, manipulating and converting BVH motion capture files.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Olaf Haag',
      author_email='contact@olafhaag.com',
      url='https://github.com/olafhaag/bvh-toolbox',
      classifiers=['License :: OSI Approved :: MIT License',
                   #'Programming Language :: Python :: 2.7',  # untested
                   'Programming Language :: Python :: 3',
                   'Operating System :: OS Independent',
                   'Environment :: Console',
                   'Development Status :: 3 - Alpha',
                   ],
      keywords='bvh BioVision mocap motion-capture convert animation 3d',
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      python_requires='>=3',
      install_requires=['numpy',
                        'transforms3d >= 0.3.1'],
      extras_require={'dev': ['sympy', 'panda3d', 'twine'],
                      'test': ['pytest', 'hypothesis'],
                      },
      entry_points={'console_scripts': ['bvh2csv=bvhtoolbox.convert.bvh2csv:main',
                                        'csv2bvh=bvhtoolbox.convert.csv2bvh:main',
                                        'bvh2egg=bvhtoolbox.convert.bvh2egg:main',
                                        'bvh2xaf=bvhtoolbox.convert.bvh2xaf:main',
                                        'bvh2xsf=bvhtoolbox.convert.bvh2xsf:main',
                                        'bvhoffsetjointangles=bvhtoolbox.manipulate.offsetjointangles:main',
                                        'bvhremoveframes=bvhtoolbox.manipulate.removeframes:main',
                                        'bvhrenamejoints=bvhtoolbox.manipulate.renamejoints:main',
                                        ],
                    },
      project_urls={'Bug Reports': 'https://github.com/olafhaag/bvh-toolbox/issues',
                    'Source': 'https://github.com/olafhaag/bvh-toolbox/',
                    },
      )
