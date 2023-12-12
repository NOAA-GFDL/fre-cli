# FRE-CLI
FMS Runtime Environment (FRE) CLI developed using Python's Click package

## Usage
* Need to set up Conda environment first and foremost
    - If on workstation:
        - module load conda
    - Create new Conda environment
        - conda create -n $envName
    - Run `conda install` on needed dependencies
        - `conda install -c noaa-gfdl fre-cli` should install the CLI package created from the meta.yaml file
    - setup.py file allows `fre.py` to be ran with `fre` in the command line instead of `python fre.py`
* Enter commands and follow `--help` messages for guidance
* Can run directly from any directory, no need to `cd` into `/fre/`
* May need to deactivate environment and reactivate it in order for changes to apply

### Tools Included
1)  fre pp
    - Postprocessing yaml configuration
    - Syntax: `fre pp configure -y [user-edit yaml file]`
    - Currently, in order to use this subtool, the user needs the following tools available: pyyaml, click, pathlib, and jsonschema
2)  fre check
3)  fre list
4)  fre make
5)  fre run
6)  fre test