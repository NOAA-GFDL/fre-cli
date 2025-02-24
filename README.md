# **`fre-cli`**

<!-- from https://anaconda.org/NOAA-GFDL/fre-cli/badges -->
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/version.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_relative_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![CI](https://github.com/NOAA-GFDL/fre-cli/workflows/publish_conda/badge.svg)](https://github.com/NOAA-GFDL/fre-cli/actions?query=workflow%3Apublish_conda+branch%3Amain++)
![Coverage Badge](https://noaa-gfdl.github.io/fre-cli/_images/cov_badge.svg)
![Pytest Badge](https://noaa-gfdl.github.io/fre-cli/_images/pytest_badge.svg)

* [Documentation](https://noaa-gfdl.github.io/fre-cli/index.html)

`fre-cli` is the Flexible Runtime Environment (`FRE`) command-line interface (`CLI`). `fre-cli` aims to gives users intuitive and easy-to-understand access to both newly developed, and legacy `FRE` tools via a `click`-driven CLI, delivered as a `conda` package.

## **Intro**
`fre-cli` is a modern, user-friendly `conda` package that allows users to call `FRE` commands via a pythonic `Click`-based interface in a **_fre_** **tool** **_subtool_** style syntax. To learn more about what that means, read the graphic below or watch the following sample video in this section

![Screenshot from 2024-04-18 13-42-04](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/43c028a6-4e6a-42fe-8bec-008b6758ea9b)

<!-- ![clidiagram](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/04cd8ce1-dec8-457f-b8b7-544275e04f46) -->

![IMG_1076](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/817cabe1-6e3b-4210-9874-b13f601265d6)

## **How to get Started**
Pick your entry-point to using `fre-cli` based on your requirements and needs. `fre-cli` is a `conda` package, and so requires
`conda` or `miniforge` (alias'd to `conda`) nearby.

### Method 1 - user-approach, Personal Conda Environment Building from uploaded Conda Package
If you're a user not at GFDL, already have `conda`, and want a `fre-cli` ready to explore out-of-the-box, one simply needs:
```
conda create --name fre --channel noaa-gfdl --channel conda-forge fre-cli
```

If you wish to specify a specific version:
```
conda create --name fre-202501 --channel noaa-gfdl --channel conda-forge fre-cli::2025.01
```

### Method 2 - contributor/developer-approach, Personal Conda Environment Building from cloned `fre-cli` repository
Developers should have a full personal environment (without `fre-cli`) and use a locally `pip`-installed copy of the code.
This enables full-featured usage of the software, equivalent to that of Method 1, but with the flexibility of being able
to reliably `pip` install a local copy of the code.

This approach can be used both in and outside of GFDL. The only difference is how one accesses `conda` commands
```
# make sure conda is available / in your PATH variable
# if you are at gfdl, access conda via Lmod / miniforge module
module load miniforge

# Append necessary channels- fre-cli needs only these two channels and no others to build.
# it's possible depending on your conda installation that additional configuration steps are needed
conda config --append channels noaa-gfdl
conda config --append channels conda-forge

# grab a copy of the code from github and cd into the repository directory
git clone --recursive https://github.com/noaa-gfdl/fre-cli.git
cd fre-cli

# to avoid being prompted for confirmation, add '-y' to the call
# this downloads/builds fre-cli's dependecies ONLY
conda env create -f environment.yml

# activate the environment you just created.
# fre-cli isn't installed yet though, ONLY dependencies
# if you changed the name of the build environment, activate that name instead of fre-cli
conda activate fre-cli

# add mkmf to your PATH
export PATH=$PATH:${PWD}/mkmf/bin

# now we pip install the local code under the `fre/` directory
# the -e flag makes re-installing the code after editing not necessary
pip install -e .
```

* All other dependencies used by the tools are installed along with this install (configured inside the meta.yaml), with the exception of local modules
* setup.py file allows [`fre.py`](https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/fre.py) to be ran with `fre` as the entry point on the command line instead of `python fre.py`
* If you want to create your OWN environment for development, testing, etc., and try out anything you want!
* This way, that local copy is the ONLY `fre-cli` in the environment. You will always know which version of the code `python` is using
    - For further notes on development and contributing to `fre-cli` see [`CONTRIBUTING.md`](https://github.com/NOAA-GFDL/fre-cli/blob/main/CONTRIBUTING.md)

### Method 3 - a User on GFDL systems (e.g. PPAN, Gaea), with `Lmod`
    - `module load fre/2025.01`
	- Pro: simplest way to access `fre-cli` at GFDL
    - Con: _Cannot install local changes on top via `pip`


### Method 4 - a User at GFDL, via Conda Environment Activation
* If you want to hit the ground running, but have some flexibility in including other things without full development options available to you:

- _Can install local changes on top via `pip`_
  - the locally installed `fre-cli` can sometimes bump into the copy living in the activated `conda` environment.
  - this approach shouldn't generally be used for concerted development efforts, but is good enough for simple and quick proto-typing.
  - for developers serious about making contributions, Method 3 below is strongly advised.
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
