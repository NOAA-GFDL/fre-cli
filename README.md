# **FRE-CLI**

FMS Runtime Environment (FRE) CLI developed using Python's Click package

## **Usage (Users)**

* Need to set up Conda environment first and foremost
    - If on workstation:
        - `module load conda`
    - Create new Conda environment
        - `conda create -n [environmentName]`
    - Run `conda install` on needed dependencies
        - `conda install noaa-gfdl::fre-cli` should install the CLI package created from the meta.yaml file located at https://anaconda.org/noaa-gfdl
        - All other dependencies used by the tools are installed along with this install (configured inside the meta.yaml), with the exception of local modules
    - setup.py file allows `fre.py` to be ran with `fre` as the entry point in the command line instead of `python fre.py`
* Enter commands and follow `--help` messages for guidance (brief rundown of commands also provided below)
    - If the user just runs `fre`, it will list all the command groups following `fre`, such as `run`, `make`, `pp`, etc. and once the user specifies a command group, the list of available subcommands for that group will be shown 
    - Commands that require arguments to run will alert user about missing arguments, and will also list the rest of the optional parameters if `--help` is executed
        - Argument flags are not positional, can be specified in any order as long as they are specified
* Can run directly from any directory, no need to clone repository
* *May need to deactivate environment and reactivate it in order for changes to apply*

### **Tools Included**

In development:
1)  **fre pp**
    - configure
        - Postprocessing yaml configuration
        - Minimal Syntax: `fre pp configure -y [user-edit yaml file]`
        - Module(s) needed: n/a
    - checkout
        - Checkout template file and clone gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git repository 
        - Minimal Syntax: `fre pp checkout -e [experiment name] -p [platform name] -t [target name]`
        - Module(s) needed: n/a
2)  **fre catalog**
    - buildCatalog
        - Builds json and csv format catalogs from user input directory path
        - Minimal Syntax: `fre catalog buildCatalog -i [input path] -o [output path]`
        - Module(s) needed: n/a

To be developed:
1)  **fre check**
2)  **fre list**
3)  **fre make**
4)  **fre run**
5)  **fre test**
6)  **fre yamltools**

## **Usage (Developers)**

* Developers are free to use the user guide above to familiarize with the CLI and save time from having to install any dependencies, but development within a Conda environment is heavily recommended regardless
* Gain access to the repository with `git clone git@github.com:NOAA-GFDL/fre-cli.git` or your fork's link (recommended) and an SSH RSA key
    - Once inside the repository, developers can test local changes by running a `pip install .` inside of the root directory to install the fre-cli package locally with the newest local changes
    - Test as a normal user would use the CLI
 
### **Adding Tools From Other Repositories**

* Currently, the solution to this task is to approach it using Conda packages. The tool that is being added must reside within a repository that contains a meta.yaml that includes Conda dependencies like the one in this repository and ideally a setup.py (may be subject to change due to deprecation) that may include any potentially needed pip dependencies
    - Once published as a Conda package, ideally on the NOAA-GFDL channel at https://anaconda.org/NOAA-GFDL, an addition can be made to the "run" section under the "requirements" category in the meta.yaml of the fre-cli following the syntax `channel:package`
