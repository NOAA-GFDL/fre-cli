# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path('..').resolve()))

from fre import __version__ as pkg_version

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'fre-cli'
copyright = f'{dt.datetime.now().year}, NOAA-GFDL MSD Workflow Team'
author = 'NOAA-GFDL MSD Workflow Team'
# special thank you to Bennett Chang for initializing the fre-cli repository
release = pkg_version   # type: ignore

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = ['sphinx.ext.autodoc']
exclude_patterns = ['fre/tests/test_files/ascii_files/*']

# Mock imports for dependencies not needed during doc build
# This allows Sphinx to build docs without installing heavy dependencies
autodoc_mock_imports = [
    'catalogbuilder',
    'cdo',
    'cftime',
    'cmor',
    'cylc',
    'cylc-flow',
    'cylc-rose',
    'metomi-rose',
    'netCDF4',
    'numpy',
    'xarray',
    'pandas',
    'intake',
    'intake-esm',
    'dask',
    'zarr',
    'boto3',
    'pytest',
    'metomi',
    'analysis_scripts',
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'renku'
