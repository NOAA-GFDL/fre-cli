Usage
=====

User Usage
----------

**Conda environment set up**

Load Conda

.. code-block::console
 module load conda

Create new Conda environment

.. code-block::console
 conda create -n [environmentName]

Append necessary channels

.. code-block::console
 conda config --append channels noaa-gfdl
 conda config --append channels conda-forge

Install needed dependencies

.. code-block::console
 conda install noaa-gfdl::fre-cli
 
setup.py file allows fre.py to be ran with fre as the entry point on the command line instead of python fre.py

Enter commands and follow *--help* messages for guidance (brief rundown of commands also provided below)

If the user just runs *fre*, it will list all the command groups following *fre*, such as *run*, *make*, *pp*, etc. and once the user specifies a command group, the list of available subcommands for that group will be shown

Commands that require arguments to run will alert user about missing arguments, and will also list the rest of the optional parameters if *--help* is executed

Argument flags are not positional, can be specified in any order as long as they are specified

Can run directly from any directory, no need to clone repository

May need to deactivate environment and reactivate it in order for changes to apply


Tools
-----

A few subtools are currently in development:

**fre pp**

1. configure 

* Postprocessing yaml configuration
* Minimal Syntax: *fre pp configure -y [user-edit yaml file]*
* Module(s) needed: n/a
* Example: *fre pp configure -y /home/$user/pp/ue2/user-edits/edits.yaml*

2. checkout

* Checkout template file and clone gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git repository
* Minimal Syntax: *fre pp checkout -e [experiment name] -p [platform name] -t [target name]*
* Module(s) needed: n/a
* Example: *fre pp checkout -e c96L65_am5f4b4r0_amip -p gfdl.ncrc5-deploy -t prod-openmp*


**fre catalog**

1. buildCatalog1
* Builds json and csv format catalogs from user input directory path
* Minimal Syntax: *fre catalog buildCatalog -i [input path] -o [output path]*
* Module(s) needed: n/a
* Example: *fre catalog buildCatalog -i /archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp -o ~/output --overwrite*

**To be developed:**

#. fre check
#. fre list
#. fre make
#. fre run
#. fre test
#. fre yamltools


Usage (Developers)
------------------

Developers are free to use the user guide above to familiarize with the CLI and save time from having to install any dependencies, but development within a Conda environment is heavily recommended regardless

Gain access to the repository with *git clone git@github.com:NOAA-GFDL/fre-cli.git* or your fork's link (recommended) and an SSH RSA key

Once inside the repository, developers can test local changes by running a *pip install .* inside of the root directory to install the fre-cli package locally with the newest local changes

Test as a normal user would use the CLI

**Adding New Tools - Checklist**

If there is *no* subdirectory created for the new tool you are trying to develop, there are a few steps to follow:

1. Create a subdirectory for the tool group inside the /fre folder; i.e. /fre/fre(subTool)

2. Add an *__init__.py* inside of the new subdirectory

* This will contain one line, *from fre.fre(subTool) import **

* The purpose of this line is to allow the subTool module to include all the scripts and functions within it when invoked by fre

3. Add a file named *fre(subTool).py*. This will serve as the main file to house all of the tool's related subcommands

4. Add a Click group named after the subTool within *fre(subTool).py*

* This group will contain all of the subcommands

5. Create separate files to house the code for each different subcommand; do not code out the full implemetation of a function inside of a Click command within *fre(subTool).py*

6. Be sure to import the contents of the needed subcommand scripts inside of fre(subTool).py

* i.e. from fre.fre(subTool).subCommandScript import *

7. At this point, you can copy and paste the parts of your main Click subcommand from its script into *fre(subTool).py* when implementing the function reflective of the subcommand function

* Everything will remain the same; i.e. arguments, options, etc.

* However, this new function within *fre(subTool).py* must a new line after the arguments, options, and other command components; *@click.pass_context*

* Along with this, a new argument "context" must now be added to the parameters of the command (preferably at the beginning, but it won't break it if it's not)

8. From here, all that needs to be added after defining the command with a name is *context.forward(mainFunctionOfSubcommand)*, and done!

9. After this step, it is important to add *from fre.fre(subTool) import* to the *__init__.py* within the /fre folder

10. The last step is to replicate the subcommand in the same way as done in *fre(subTool).py* inside of *fre.py*, but make sure to add *from fre import fre(subTool)* and *from fre.fre(subTool).fre(subTool) import **

Please refer to this issue when encountering naming issues: `NOAA-GFDL#31 <https://github.com/NOAA-GFDL/fre-cli/issues/31>`_

**Adding Tools From Other Repositories**

Currently, the solution to this task is to approach it using Conda packages. The tool that is being added must reside within a repository that contains a meta.yaml that includes Conda dependencies like the one in this repository and ideally a setup.py (may be subject to change due to deprecation) that may include any potentially needed pip dependencies

* Once published as a Conda package, ideally on the NOAA-GFDL channel at https://anaconda.org/NOAA-GFDL, an addition can be made to the "run" section under the "requirements" category in the meta.yaml of the fre-cli following the syntax channel::package

* On pushes to the main branch, the package located at https://anaconda.org/NOAA-GFDL/fre-cli will automatically be updated using the workflow file

**MANIFEST.in**

In the case where non-python files like templates, examples, and outputs are to be included in the fre-cli package, MANIFEST.in can provide the solution. Ensure that the file exists within the correct folder, and add a line to the MANIFEST.in file saying something like *include fre/fre(subTool)/fileName.fileExtension*

* For more efficiency, if there are multiple files of the same type needed, the MANIFEST.in addition can be something like *recursive-include fre/fre(subTool) *.fileExtension* which would recursively include every file matching that fileExtension within the specified directory and its respective subdirectories.

**Example /fre Directory Structure**
.
├── __init__.py
├── fre.py
├── fre(subTool)
│   ├── __init__.py
│   ├── subCommandScript.py
│   └── fre(subTool).py
