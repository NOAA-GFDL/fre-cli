.. _setup:

=====
Setup
=====
FRE-cli is deployed on NOAA RDHPCS and GFDL systems as Environment Modules and is
conda-installable from the ``noaa-gfdl`` anaconda channel for use on any system.

Loading FRE-cli on NOAA-GFDL systems
=====================================

The GFDL Workflow Team deploys fre-cli as an Environment Module on GFDL workstations, PPAN,
and Gaea.

At GFDL (workstations and PPAN):

.. code-block:: console

 module load fre/<version>

On Gaea, the FRE modulefiles must be added to the module search path first:

.. code-block:: console

 module use -a /ncrc/home2/fms/local/modulefiles
 module load fre/<version>

Replace ``<version>`` with the desired release (e.g. ``2026.01``).

Installing FRE-cli on generic systems
======================================

On any system with conda available, fre-cli can be installed from the ``noaa-gfdl`` anaconda
channel:

.. code-block:: console

 conda config --append channels noaa-gfdl
 conda config --append channels conda-forge
 conda create --name fre-<version> --channel noaa-gfdl --channel conda-forge fre-cli::<version>
 conda activate fre-<version>

Replace ``<version>`` with the desired release (e.g. ``2026.01``).

Using the container
===================

.. include:: container.rst
