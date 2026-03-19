============
Glossary
============

.. glossary::
  :sorted:

  target
    The term refers to the ``fre make`` argument which defines compiler options to turn on during compilation.
    ``fre-cli`` requires either ``prod``, ``repro``, or ``debug`` followed by any number of supplementary options
    separated by a ``-`` such as ``openmp`` and ``lto``. For example: ``repro-openmp``, ``prod-openmp-lto``

  platform
    The term refers to the ``fre make`` argument which indicates the computing platform and compiler and its version.
    This commonly takes on the form ``platform.compiler`` (.e.g. ``ncrc5.intel25``, ``gfdl.intel25``). Note, the
    platform must be defined in ``platforms.yaml``. See `fre-examples: platforms.yaml
    <https://github.com/NOAA-GFDL/fre-examples/blob/main/platforms.yaml>`_

  makefile
    The term refers to the file created, for both the bare-metal and container builds, through ``fre make makefile``.
    This file defines required components, dependencies, any necessary linker flags, and the mk_template used for the
    model to compile. The mk_template path is defined in the platforms yaml and refers to a template in the `mkmf repository
    <https://github.com/NOAA-GFDL/mkmf>`_.
