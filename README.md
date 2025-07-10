# **`fre-cli`**

<!-- from https://anaconda.org/NOAA-GFDL/fre-cli/badges -->
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/version.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_relative_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)

[![CI](https://github.com/NOAA-GFDL/fre-cli/workflows/publish_conda/badge.svg)](https://github.com/NOAA-GFDL/fre-cli/actions?query=workflow%3Apublish_conda+branch%3Amain++)
[![readthedocs](https://app.readthedocs.org/projects/noaa-gfdl-fre-cli/badge/?version=latest&style=flat)](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/)
[![codecov](https://codecov.io/gh/NOAA-GFDL/fre-cli/branch/ghpages.deprecation/graph/badge.svg?token=iGb0wEuWs1)](https://codecov.io/gh/NOAA-GFDL/fre-cli)

* [Documentation](https://noaa-gfdl.github.io/fre-cli/index.html)

`fre-cli` is the Flexible Runtime Environment (`FRE`) command-line interface (`CLI`). `fre-cli` aims to gives users intuitive and 
easy-to-understand access to both newly developed, and legacy `FRE` tools via a `click`-driven CLI, delivered as a `conda` package.



## **Intro**
`fre-cli` is a modern, user-friendly `conda` package that allows users to call `FRE` commands via a pythonic `Click`-based interface 
in a **_fre_** **tool** **_subtool_** style syntax. To learn more about what that means, read the graphic below or watch the following
sample video in this section

![Screenshot from 2024-04-18 13-42-04](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/43c028a6-4e6a-42fe-8bec-008b6758ea9b)

![IMG_1076](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/817cabe1-6e3b-4210-9874-b13f601265d6)



## **How to get Started**
Pick your entry-point to using `fre-cli` based on your requirements and needs. `fre-cli` is a `conda` package, and so requires
`conda` or `miniforge` (alias'd to `conda`) nearby.


### Method 1 - user-approach, Personal Conda Environment via conda channel/package
If you're a user not at GFDL, already have `conda`, and want a `fre-cli` that's ready-to-go out-of-the-box, simply do:
```
conda create --name fre --channel noaa-gfdl --channel conda-forge fre-cli
```

If you wish to specify aversion:
```
conda create --name fre-202501 --channel noaa-gfdl --channel conda-forge fre-cli::2025.01
```


### Method 2 - developer-approach, Personal Conda Environment via repo clone
Developers should have a full personal environment (without `fre-cli`) and use a locally `pip`-installed copy of the code. This 
enables full-featured usage of the software, equivalent to that of Method 1, but with the flexibility of being able to reliably 
`pip` install a local copy of the code.

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


### Method 3 - a User on GFDL systems (e.g. PPAN, Gaea), with `Lmod`
If you do not wish to interface with `conda` at all, but desire access to `fre` commands, simply execute `module load fre/2025.01`,
and you're ready to go. This is the simplest way to access `fre-cli` at GFDL, but does not easily facillitate `fre-cli` development.


### Method 4 - a User at GFDL, via Conda Environment Activation
If you want to hit the ground running, but have some flexibility being able to utilize local python code with `fre-cli` environment, 
this option can work for you. Developers can also utilize this approach for rapid-prototyping, but it's reccomended to switch to 
Method 1 for finalizing contributions.

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

## GFDL deployment notes
Presently, all PRs accepted for merging to `main` trigger a conda-package deployment to the 
[`noaa-gfdl` channel](https://anaconda.org/NOAA-GFDL/fre-cli), with the latest package version. 

### Latest available release (`fre/test`)
GFDL and gaea's `fre-cli` is re-built and re-installed as a conda environment/package every night at midnight into the `fms` user spaces.
```
# at GFDL or gaea, access with Lmod
module load fre/test

# at gaea, access with conda activation
conda activate /ncrc/home/fms/conda/envs/fre-test

# at GFDL, access with conda activation
conda activate /nbhome/fms/conda/envs/fre-test
```

### Major releases (`fre/2025.NN`)
These deployments are currently hand-installed in the `fms` user directories.
```
# at GFDL or gaea, access with Lmod
module load fre/2025.NN

# at gaea, access with conda activation
conda activate /ncrc/home/fms/conda/envs/fre-2025.NN

# at GFDL, access with conda activation
conda activate /nbhome/fms/conda/envs/fre-2025.NN
```



### Patch releases (`fre/2025.NN.PP`)
These deployments are hand-installed to the same major-release location, overwriting them. 
```
# at GFDL or gaea, access with Lmod
module load fre/2025.NN

# at gaea, access with conda activation
conda activate /ncrc/home/fms/conda/envs/fre-2025.NN

# at GFDL, access with conda activation
conda activate /nbhome/fms/conda/envs/fre-2025.NN
```

### Which `fre` version do I have?
You can always check the specific version, down to the patch-release space, with 
```
$ ] fre --version
fre, version 2025.NN.PP
```

# Disclaimer
The United States Department of Commerce (DOC) GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. DOC has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any claims against the Department of Commerce stemming from the use of its GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.

