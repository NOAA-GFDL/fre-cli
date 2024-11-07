=====
Setup
=====
fre-cli is conda-installable from the “noaa-gfdl” anaconda channel.

On GFDL systems
========================
If you are at GFDL (gaea, PP/AN, workstations), you may skip installation as modules are available:

``module load fre/2024.01``

``fre --help``

Generic
=======================
If you are outside GFDL or are a FRE developer, it's easy to install through conda. If you're at GFDL,

``module load miniforge``

If you are outside, install the miniconda tool with the standard instructions (https://docs.anaconda.com/miniconda/miniconda-install/).

Then, install the latest fre-cli from the NOAA-GFDL anaconda channel (https://anaconda.org/NOAA-GFDL/fre-cli):

``conda create --name fre --channel noaa-gfdl --channel conda-forge fre-cli``

To install a specific version,

``conda create --name fre-202401 --channel noaa-gfdl --channel conda-forge fre-cli::2024.01``

and activate it:

``conda activate fre``

``fre --help``
