Setup
=====

Set up Conda environment
------------------------

If on workstation:

``module load conda``

Create new Conda environment:

``conda create -n [environmentName]``

Append necessary channels:

``conda config --append channels noaa-gfdl; conda config --append channels conda-forge;``

Run conda install on needed dependencies, should install the CLI package located at
`the GFDL conda channel https://anaconda.org/NOAA-GFDL/fre-cli`_ :

``conda install noaa-gfdl::fre-cli``

* ``fre/setup.py`` allows ``fre/fre.py`` to be ran as ``fre`` on the command line by defining it as
  an **entry point**. Without it, the call would be, instead, ``python fre/fre.py``
