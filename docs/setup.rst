=====
Setup
=====
fre-cli is conda-installable from the “noaa-gfdl” anaconda channel (https://anaconda.org/NOAA-GFDL/fre-cli)
and is deployed on GFDL systems as Environment Modules.

On GFDL systems
========================
If you are at GFDL (gaea, PP/AN, workstations), you may skip installation:

``module load fre/2024.01``

``fre --help``

Generic
=======================
If you are outside GFDL or are a FRE developer, install with conda. If you're at GFDL, bring conda into your PATH with

``module load miniforge``

If you are outside GFDL, install the miniconda tool with the standard instructions (https://docs.anaconda.com/miniconda/miniconda-install/).

Once you have conda available, install the latest fre-cli from the NOAA-GFDL anaconda channel:

``conda create --name fre --channel noaa-gfdl --channel conda-forge fre-cli``

To install a specific version,

``conda create --name fre-202401 --channel noaa-gfdl --channel conda-forge fre-cli::2024.01``

and activate it:

``conda activate fre``

``fre --help``
