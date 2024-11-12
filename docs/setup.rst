.. NEEDS UPDATING #TODO
=====
Setup
=====

Set up Conda environment
========================

various options work quite well:


If on workstation
-----------------

``module load fre/2024.01``


Create New Conda environment
----------------------------

if you're at GFDL:
``module load miniforge``

create an empty environment to start
``conda create -n [environmentName]``

activate the empty environment:
``conda activate [environmentName]``

append necessary channels:
``conda config --append channels noaa-gfdl; conda config --append channels conda-forge;``

install ``fre-cli`` into the activated environment from `the GFDL conda channel <https://anaconda.org/NOAA-GFDL/fre-cli>`_ :
``conda install noaa-gfdl::fre-cli``

YAML Framework
========================
In order to utilize FRE Canopy tools, a distrubuted YAML structure is required. 
