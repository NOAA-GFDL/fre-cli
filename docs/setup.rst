=====
Setup
=====
FRE-cli is conda-installable from the “noaa-gfdl” anaconda channel (https://anaconda.org/NOAA-GFDL/fre-cli)
and is deployed on GFDL systems as Environment Modules.

On GFDL systems
===============

use Lmod
--------
If you are at GFDL (gaea, PPAN, workstations), you may skip installation by using Lmod::

  module load fre/2025.01
  fre --help

use conda
---------
If you are at GFDL (gaea, PPAN, workstations), you may activate the environments used by the modules directly with conda::

  # get conda in your PATH
  module load miniforge

  # if on PPAN or workstation
  conda activate

  # if on gaea
  conda activate 

Build-your-own FRE environment
==============================
If you are outside GFDL, you must manage and configure your own installation of conda and/or miniforge. If you're at GFDL, bring conda into your PATH like so::

  module load miniforge

create environment from uploaded conda package
----------------------------------------------
If one is not interested in contributing to FRE or developing fre-cli, the simplest approach is to grab the latest fre-cli from the NOAA-GFDL anaconda channel::

  conda create --name fre --channel noaa-gfdl --channel conda-forge fre-cli

  # to grab a specific version, instead do:
  conda create --name fre-202501 --channel noaa-gfdl --channel conda-forge fre-cli::2025.01

and activate it::

  conda activate fre

confirm the environment and package was build successfully with::

  fre --help

create environment from github repo clone
-----------------------------------------
If one is interested in contributing to FRE and wishes to develop features and have user-like functionality, it's recommended to download and use the code from the repository directly.
Assuming one has `conda` in their paths, then do the following::

  # Append necessary channels- fre-cli needs only these two channels and no others to build.
  # it's possible depending on your conda installation that additional configuration steps are needed
  conda config --append channels noaa-gfdl
  conda config --append channels conda-forge

  # grab a copy of the code from github and cd into the repository directory
  git clone --recursive https://github.com/noaa-gfdl/fre-cli.git
  cd fre-cli

  # to avoid being prompted for confirmation, add '-y' to the call
  # this downloads/builds fre-cli's dependecies ONLY
  conda env create -f environment.yml

  # activate the environment you just created.
  # fre-cli isn't installed yet though, ONLY dependencies
  # if you changed the name of the build environment, activate that name instead of fre-cli
  conda activate fre-cli

  # add mkmf to your PATH
  export PATH=$PATH:${PWD}/mkmf/bin

  # now we pip install the local code under the `fre/` directory
  # the -e flag makes re-installing the code after editing not necessary
  pip install -e .
