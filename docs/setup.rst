.. _setup:

=====
Setup
=====
FRE-cli is conda-installable from the “noaa-gfdl” anaconda channel (https://anaconda.org/NOAA-GFDL/fre-cli)
and is deployed on NOAA RDHPCS and GFDL systems as Environment Modules.

Installing FRE-cli
==================

Instructions for installing fre-cli on GFDL and NOAA RDHPCS systems via lmod and on any system via conda can be found in the `fre-cli repository README <https://github.com/NOAA-GFDL/fre-cli/blob/main/README.md>`__.


Install FRE-cli from local GitHub clone (for development)
=========================================================

When contributing to FRE, it is recommended to download and use the code from the repository directly to test changes.
Assuming one has ``conda`` in their path, then do the following::

  # Append necessary channels- fre-cli needs only these two channels and no others to build.
  # it's possible depending on your conda installation that additional configuration steps are needed
  conda config --append channels noaa-gfdl
  conda config --append channels conda-forge

  # grab a copy of the code from github and cd into the repository directory
  git clone --recursive https://github.com/noaa-gfdl/fre-cli.git
  cd fre-cli

  # to avoid being prompted for confirmation, add '-y' to the call
  # this downloads/builds fre-cli's dependencies ONLY
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
