[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/version.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![Anaconda-Server Badge](https://anaconda.org/noaa-gfdl/fre-cli/badges/latest_release_relative_date.svg)](https://anaconda.org/noaa-gfdl/fre-cli)
[![CI](https://github.com/NOAA-GFDL/fre-cli/workflows/publish_conda/badge.svg)](https://github.com/NOAA-GFDL/fre-cli/actions?query=workflow%3Apublish_conda+branch%3Amain++)
[![readthedocs](https://app.readthedocs.org/projects/noaa-gfdl-fre-cli/badge/?version=latest&style=flat)](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/)
[![codecov](https://codecov.io/gh/NOAA-GFDL/fre-cli/graph/badge.svg?token=iGb0wEuWs1)](https://codecov.io/gh/NOAA-GFDL/fre-cli)

# **`fre-cli`**

`fre-cli` is GFDL's next-generation FMS Runtime Environment (`FRE`) command-line interface (`CLI`). `fre-cli` aims to gives users intuitive and easy-to-understand access to both newly developed, and legacy `FRE` tools via a `click`-driven CLI, delivered as a `conda` package.

## **Where to find information**

[Fre-cli Documentation](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/index.html) is hosted on `readthedocs`

## **Intro**
`fre-cli` is a modern, user-friendly `conda` package that allows users to call `FRE` commands via a pythonic `Click`-based interface in a **_fre_** **tool** **_subtool_** style syntax. To learn more about what that means, read the graphic below or watch the following sample video in this section

![Screenshot from 2024-04-18 13-42-04](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/43c028a6-4e6a-42fe-8bec-008b6758ea9b)

![IMG_1076](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/817cabe1-6e3b-4210-9874-b13f601265d6)

## **Quickstart**

`fre-cli` is conda-installable from the “noaa-gfdl” anaconda channel (https://anaconda.org/NOAA-GFDL/fre-cli)
and is deployed on RDHPCS and GFDL systems as Environment Modules.

### On NOAA RDHPCS Gaea and at GFDL on PPAN

```
module use -a /ncrc/home2/fms/local/modulefiles
module load fre/2025.04
```

## Install via Conda

```
conda config --append channels noaa-gfdl
conda config --append channels conda-forge
conda create --name fre-2025.04 --channel noaa-gfdl --channel conda-forge fre-cli::2025.04
conda activate fre-2025.04
```

## GFDL/RDHPCS deployment notes
Presently, all PRs accepted for merging to `main` trigger a conda-package deployment to the 
[`noaa-gfdl` channel](https://anaconda.org/NOAA-GFDL/fre-cli), with the latest package version. 

### Latest available release (`fre/test`)
GFDL and gaea's `fre-cli` is re-built and re-installed as a conda environment/package every night at midnight into the `fms` user spaces.
```
# at GFDL or gaea, access with Lmod
module load fre/test
```

### Major releases (`fre/YYYY.NN`)
These deployments are currently installed by tyhe GFDL workflow team in the `fms` user directories.
```
# at GFDL or gaea, access with Lmod
module load fre/YYYY.NN
```

### Patch releases (`fre/YYYY.NN.PP`)
These deployments are hand-installed to the same major-release location, overwriting them. 
```
# at GFDL or gaea, access with Lmod
module load fre/YYYY.NN
```

### Which `fre` version do I have?
You can always check the specific version, down to the patch-release space, with 
```
$ ] fre --version
fre, version YYYY.NN.PP
```

# Disclaimer
The United States Department of Commerce (DOC) GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. DOC has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any claims against the Department of Commerce stemming from the use of its GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.

