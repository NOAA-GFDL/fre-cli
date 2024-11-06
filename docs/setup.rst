Setup
=====

Set up Conda environment first and foremost

If on workstation:
``module load conda``

Create new Conda environment:
``conda create -n [environmentName]``

Append necessary channels:
``conda config --append channels noaa-gfdl; conda config --append channels conda-forge;``

Run conda install on needed dependencies, should install the CLI package located at
`the GFDL conda channel https://anaconda.org/NOAA-GFDL/fre-cli`_ :
``conda install noaa-gfdl::fre-cli``

All other dependencies used by the tools are installed along with this install (configured inside the meta.yaml), with the exception of local modules
setup.py file allows fre.py to be ran with fre as the entry point on the command line instead of python fre.py

Enter commands and follow --help messages for guidance (brief rundown of commands also provided below)

If the user just runs fre, it will list all the command groups following fre, such as run, make, pp, etc. and once the user specifies a command group, the list of available subcommands for that group will be shown

Commands that require arguments to run will alert user about missing arguments, and will also list the rest of the optional parameters if --help is executed

Argument flags are not positional, can be specified in any order as long as they are specified

Can run directly from any directory, no need to clone repository

May need to deactivate environment and reactivate it in order for changes to apply
