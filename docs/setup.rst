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
In order to utilize FRE Canopy tools, a distrubuted YAML structure is required. This framework includes a main model yaml, a compile yaml, a platforms yaml, and post-processing yamls. 

Model Yaml
-----------------

The model yaml defines reusable variables, shared directories, switches, and post-processing settings, and paths to compile and post-processing yamls.  

Compile Yaml
-----------------

The compile yaml defines compilation information including copmonent names, repos, branches, necessary flags, and necessary overrides. In order to create the compile yaml, one can refer to compile information defined in an XML.


Platform Yaml
_________________

The platform yaml defines information for both bare-metal and container platforms. Information includes the platform name, the compiler used, necessary modules to load, an mk template, fc, cc, container build, and container run.

Post-Processing Yaml
-----------------

The post-processing yamls include information specific to experiments, such as directories to data and other scripts used, switches, and component information. 

