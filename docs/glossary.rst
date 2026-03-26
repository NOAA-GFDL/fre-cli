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

  Makefile
    A Makefile is a configuration file required for code compilation with GNU make. For bare-metal and container
    builds, this file is created with the ``fre make makefile`` subtool. The Makefile contains information about
    the required components, library dependencies, linker flags, compiler flags, and the mk_template (defined in
    the ``platforms.yaml``). 
