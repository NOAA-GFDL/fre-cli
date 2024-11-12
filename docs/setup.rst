=====
Setup
=====
fre-cli is conda-installable from the “noaa-gfdl” anaconda channel (https://anaconda.org/NOAA-GFDL/fre-cli)
and is deployed on GFDL systems as Environment Modules.

On GFDL systems
========================
If you are at GFDL (gaea, PP/AN, workstations), you may skip installation::

  module load fre/2024.01

  fre --help

Generic
=======================
If you are outside GFDL or are a FRE developer, install with conda. If you're at GFDL, bring conda into your PATH::

  module load miniforge

If you are outside GFDL, install the miniconda tool with the standard instructions (https://docs.anaconda.com/miniconda/miniconda-install/).

Once you have conda available, install the latest fre-cli from the NOAA-GFDL anaconda channel::

  conda create --name fre --channel noaa-gfdl --channel conda-forge fre-cli

To install a specific version::

  conda create --name fre-202401 --channel noaa-gfdl --channel conda-forge fre-cli::2024.01

and activate it::

  conda activate fre

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

=======
  fre --help
