<!-- from https://anaconda.org/NOAA-GFDL/fre-cli/badges -->
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/version.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_relative_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![CI](https://github.com/NOAA-GFDL/fre-cli/workflows/publish_conda/badge.svg)](https://github.com/NOAA-GFDL/fre-cli/actions?query=workflow%3Apublish_conda+branch%3Amain++)
![Coverage Badge](https://noaa-gfdl.github.io/fre-cli/_images/cov_badge.svg)
![Pytest Badge](https://noaa-gfdl.github.io/fre-cli/_images/pytest_badge.svg)

# **FRE-CLI**

FMS Runtime Environment (FRE) CLI developed using Python's Click package

* [Sphinx Documentation](https://noaa-gfdl.github.io/fre-cli/index.html)

[Project Outline](https://docs.google.com/document/d/19Uc01IPuuIuMtOyAvxXj9Mn6Ivc5Ql6NZ-Q6I8YowRI/edit?usp=sharing) -->

![IMG_1076](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/817cabe1-6e3b-4210-9874-b13f601265d6)

## **Background**
`fre-cli` is a modern, user-friendly CLI that will allow users to call FRE commands using a **_fre_** **tool** _subtool_ syntax. Leveraging Click, an easily installable Python package available via PyPI and/or Conda, `fre-cli` gives users intuitive and easy-to-understand access to many FRE tools and workflows from one packaged, centralized CLI.

![Screenshot from 2024-04-18 13-42-04](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/43c028a6-4e6a-42fe-8bec-008b6758ea9b)

![clidiagram](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/04cd8ce1-dec8-457f-b8b7-544275e04f46)

## **Usage Notes**


### (Method 1) User - with Lmod
* If you want to hit the ground running:
    - _Cannot install local changes on top via `pip`_
    - GFDL Workstation: `module load fre/canopy`
    - Gaea: `module load fre/canopy`
	- Pro: simplest way to access `fre-cli` at GFDL
	- Con: not much flexibility, what you load is what you get


### (Method 2) User - Conda Environment Activation
* If you want to hit the ground running, but have some flexibility in including other things without full development options available to you:

    - _Can install local changes on top via `pip`_
    - GFDL Workstation:
        ```
        module load miniforge
        conda activate /nbhome/fms/conda/envs/fre-cli
        ```
    - Gaea:
        ```
        module use /usw/conda/modulefiles
        module load miniforge
        conda activate /ncrc/home2/Flexible.Modeling.System/conda/envs/fre-cli
        ```


### (Method 3) Developer - Conda Environment Building
* If you have Conda loaded and want to create your OWN environment for development, testing, etc.:

    - _Can install local changes on top via `pip`_
    - Steps:
        ```
        # make sure conda is in your PATH
        # at gfdl, this can be done like
        module load miniforge
        
        # Append necessary channels.
        conda config --append channels noaa-gfdl
        conda config --append channels conda-forge

        # grab a copy of the code
        git clone --recursive https://github.com/noaa-gfdl/fre-cli.git
        cd fre-cli

        # edit the name of the environment in this yaml file if desired
        # to avoid being prompted for confirmation, add '-y' to the call
        conda env create -f environment.yml

        # activate the environment you just created.
        # fre-cli isn't installed yet though, just the dependences
        # if you edited the name above, activate that name instead
        conda activate fre-cli

        # add mkmf to your PATH
        export PATH=$PATH:${PWD}/mkmf/bin

        # the -e flag pip installs the locally-editable code
		# this makes re-installing after editing code is not necessary
        pip install -e .
        ```
    - All other dependencies used by the tools are installed along with this install (configured inside the meta.yaml), with the exception of local modules
    - setup.py file allows [`fre.py`](https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/fre.py) to be ran with `fre` as the entry point on the command line instead of `python fre.py`
    - For further notes on development and contributing to `fre-cli` see [`CONTRIBUTING.md`](https://github.com/NOAA-GFDL/fre-cli/blob/main/CONTRIBUTING.md)


### Instructions for minting new releases

1. Update the package release number (i.e. reported by fre --version) and merge to `main`
- [ ] edit `version` in setup.py
- [ ] edit two version mentions in fre/tests/test_fre_cli.py

2. Create tag in fre-cli (this repository) and associated github release
- [ ] `git tag -a <release>` and `git push --tags`
- [ ] https://github.com/NOAA-GFDL/fre-cli/releases

3. Create corresponding tag in fre-workflows
- [ ] https://github.com/NOAA-GFDL/fre-workflows/tags

4. Observe new conda package deployed to noaa-gfdl channel
- [ ] https://anaconda.org/NOAA-GFDL/fre-cli

### GFDL deployment notes

Presently, all pushes to `main` trigger a conda deployment to the `noaa-gfdl` channel (https://anaconda.org/NOAA-GFDL/fre-cli),
with the latest package version.


* Latest available (`fre/test`)

An updated fre-cli installation on GFDL and gaea is reinstalled every night at midnight
into the fms user spaces:

on gaea: `/ncrc/home/fms/conda/envs/fre-test`
at GFDL: `/nbhome/fms/conda/envs/fre-test`

The `fre/test` module brings the `fre` executable into the `PATH`.

* Major release (`fre/2025.NN`)

These deployments are hand-installed in the fms user directories:

on gaea: `/ncrc/home/fms/conda/envs/fre-2025.NN`
at GFDL: `/nbhome/fms/conda/envs/fre-2025.NN`

The `fre/2025.NN` modulefiles bring the `fre` executable into the `PATH`.

```
fre --version
fre, version 2025.<NN>
```

* Patch release (`fre/2025.NN.PP`)

These deployments are hand-installed to the same major-release location,
overwriting them.

on gaea: `/ncrc/home/fms/conda/envs/fre-2025.NN`
at GFDL: `/nbhome/fms/conda/envs/fre-2025.NN`

The `fre/2025.NN` modulefiles bring the `fre` executable into the `PATH`.
Use `fre --version` to report the patch number.

```
fre --version
fre, version 2025.NN.PP
```
