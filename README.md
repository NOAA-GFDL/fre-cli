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

## Developer notes

### Instructions for new releases

1. Update the package release number (i.e. reported by fre --version) and merge to `main`
[ ] - edit `version` in setup.py
[ ] - edit two version mentions in fre/tests/test_fre_cli.py

2. Create tag in fre-cli (this repository) and associated github release
[ ] - `git tag -a <release>` and `git push --tags`
[ ] - https://github.com/NOAA-GFDL/fre-cli/releases

3. Create corresponding tag in fre-workflows
[ ] - https://github.com/NOAA-GFDL/fre-workflows/tags

4. Observe new conda package deployed to noaa-gfdl channel
[ ] - https://anaconda.org/NOAA-GFDL/fre-cli

### GFDL deployment notes

Presently, all pushes to `main` trigger a conda deployment to the noaa-gfdl channel (https://anaconda.org/NOAA-GFDL/fre-cli),
with the latest package version.

* Latest available (fre/test)

An updated fre-cli installation on GFDL and gaea is reinstalled every night at midnight
into the fms user spaces:

on gaea: /ncrc/home/fms/conda/envs/fre-test
at GFDL: /nbhome/fms/conda/envs/fre-test

The fre/test module brings the `fre` executable into the PATH.

* Major release (fre/2025.NN)

These deployments are hand-installed in the fms user directories:

on gaea: /ncrc/home/fms/conda/envs/fre-2025.NN
at GFDL: /nbhome/fms/conda/envs/fre-2025.NN

The fre/2025.NN modulefiles bring the `fre` executable into the PATH.

```
fre --version
fre, version 2025.<NN>
```

* Patch release (fre/2025.NN.PP)

These deployments are hand-installed to the same major-release location,
overwriting them.

on gaea: /ncrc/home/fms/conda/envs/fre-2025.NN
at GFDL: /nbhome/fms/conda/envs/fre-2025.NN

The fre/2025.NN modulefiles bring the `fre` executable into the PATH.

```
fre --version
fre, version 2025.<NN>.<PP>
```
