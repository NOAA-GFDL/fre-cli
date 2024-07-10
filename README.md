# **FRE-CLI**

FMS Runtime Environment (FRE) CLI developed using Python's Click package

* [Sphinx Page](https://noaa-gfdl.github.io/fre-cli/index.html)
* [Project Outline](https://docs.google.com/document/d/19Uc01IPuuIuMtOyAvxXj9Mn6Ivc5Ql6NZ-Q6I8YowRI/edit?usp=sharing)

![IMG_1076](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/817cabe1-6e3b-4210-9874-b13f601265d6)

## **Background**

As part of fre/canopy, MSD wanted to develop a modern, user-friendly CLI that will allow users to call upon FRE commands using a **_fre_** **tool** _subtool_ syntax. Developed with Click, a Python package easily installable through PyPI and Conda, the main goal of this is to allow users access to most, if not all of MSD-managed tools and workflows from one packaged, centralized CLI.

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

After one of the above, one can enter commands and follow `--help` messages for guidance. A brief rundown of commands to be provided are within each tool's folder as a `README.md`

## **Checklist: Currently Implemented Tools**

To be developed:
- [ ]  **fre check**
- [x]  **fre app**
- [x]  **fre catalog**
- [ ]  **fre list**
- [x]  **fre make**
- [x]  **fre cmor**
- [ ]  **fre run**
- [ ]  **fre test**
- [ ]  **fre yamltools**

## ** Contributing to fre-cli **

See [`CONTRIBUTING.md`](https://github.com/NOAA-GFDL/fre-cli/blob/breakup_README/CONTRIBUTING.md)
