<!-- from https://anaconda.org/NOAA-GFDL/fre-cli/badges -->
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/version.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_relative_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![CI](https://github.com/NOAA-GFDL/fre-cli/workflows/publish_conda/badge.svg)](https://github.com/NOAA-GFDL/fre-cli/actions?query=workflow%3Apublish_conda+branch%3Amain++)

<!-- ... someday... 
[![Code coverage](https://codecov.io/gh/NOAA-GFDL/fre-cli/branch/main/graph/badge.svg?flag=unittests)](https://codecov.io/gh/NOAA-GFDL/fre-cli)--> 

# **FRE-CLI**

FMS Runtime Environment (FRE) CLI developed using Python's Click package

* [Sphinx Documentation](https://noaa-gfdl.github.io/fre-cli/index.html)
<!--* ... internal doc, should remove, if anything...
[Project Outline](https://docs.google.com/document/d/19Uc01IPuuIuMtOyAvxXj9Mn6Ivc5Ql6NZ-Q6I8YowRI/edit?usp=sharing) -->

![IMG_1076](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/817cabe1-6e3b-4210-9874-b13f601265d6)

## **Background**
`fre-cli` is a modern, user-friendly CLI that will allow users to call FRE commands using a **_fre_** **tool** _subtool_ syntax. Leveraging Click, an easily installable Python package available via PyPI and/or Conda, `fre-cli` gives users intuitive and easy-to-understand access to many FRE tools and workflows from one packaged, centralized CLI.

![Screenshot from 2024-04-18 13-42-04](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/43c028a6-4e6a-42fe-8bec-008b6758ea9b)

![clidiagram](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/04cd8ce1-dec8-457f-b8b7-544275e04f46)

## **Usage (Users)**

### (Method 1) User - with Lmod

* If you want to hit the ground running:
    - _Cannot install local changes on top via `pip`_
    - GFDL Workstation: `module load fre/canopy`
    - Gaea: `module load fre/canopy`
    
### (Method 2) User - Conda Environment Activation
* If you want to hit the ground running, but have some flexibility in including other things without full development options available to you:

    - _Can install local changes on top via `pip`_
    - GFDL Workstation:
        - `module load miniforge`
        - `conda activate /nbhome/fms/conda/envs/fre-cli`
    - Gaea:
        - `module load miniforge`
        - `conda activate /ncrc/home2/Flexible.Modeling.System/conda/envs/fre-cli`
        
### (Method 3) Developer - Conda Environment Building
* If you have Conda loaded and want to create your OWN environment for development, testing, etc.:

    - _Can install local changes on top via `pip`_
    - Create a new Conda environment: `conda create -n [environmentName]`
    - Append necessary channels
        - `conda config --append channels noaa-gfdl` 
        - `conda config --append channels conda-forge`
    - Run `conda install` on needed dependencies (`conda install click` will give you access to pip as well)
        - `conda install noaa-gfdl::fre-cli` should install the [CLI package](https://anaconda.org/NOAA-GFDL/fre-cli) created from the [`meta.yaml`](https://github.com/NOAA-GFDL/fre-cli/blob/refactoring/meta.yaml)
    - All other dependencies used by the tools are installed along with this install (configured inside the meta.yaml), with the exception of local modules
    - setup.py file allows [`fre.py`](https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/fre.py) to be ran with `fre` as the entry point on the command line instead of `python fre.py`
    - For further notes on development and contributing to `fre-cli` see [`CONTRIBUTING.md`](https://github.com/NOAA-GFDL/fre-cli/blob/breakup_README/CONTRIBUTING.md)

After one of the above, one can enter commands and follow `--help` messages for guidance. A brief rundown of commands to be provided are within each tool's folder as a `README.md`

### Further Notes on Use
Following the instructions above, the user will be able to run `fre` from any directory, listing all command groups. These include e.g. `run`, `make`, and `pp`. The list of available subcommands for each group will be shown upon inclusion of the `--help` flag. The user will be alerted to any missing arguments required subcomands. Optional arguments will only shown with `--help` added to the subcommand. Note that argument flags are not positional, and can be specified in any order. 

## **Checklist: Currently Implemented Tools**

To be developed:

- [x]  **fre app**
- [x]  **fre catalog**
- [ ]  **fre check**
- [x]  **fre cmor**
- [ ]  **fre list**
- [x]  **fre make**
- [x]  **fre pp**
- [ ]  **fre run**
- [ ]  **fre test**
- [ ]  **fre yamltools**
