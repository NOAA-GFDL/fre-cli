=====
Setup
=====

Set up Conda environment
========================

various options work quite well:


If on workstation
-----------------

``module load fre/canopy``


Create new Conda environment
----------------------------
``conda create -n [environmentName]``

activate:
``conda activate [environmentName]``

append necessary channels:
``conda config --append channels noaa-gfdl; conda config --append channels conda-forge;``

install ``fre-cli`` into the activated environment from `the GFDL conda channel https://anaconda.org/NOAA-GFDL/fre-cli`_ :
``conda install noaa-gfdl::fre-cli``

