============
Glossary
============

.. glossary::
  :sorted:

  target
    The term refers to macros that modify compiler flags used in the model build. This is an
    `mkmf <https://github.com/NOAA-GFDL/mkmf/tree/main>`_ term.  The target macros are defined in
    `mkmf template files <https://github.com/NOAA-GFDL/mkmf/tree/main/templates>`_. In the fre-cli workflow, the
    platforms.yaml explicitly defines a template file which is used by mkmf to define compiler flags. fre-cli requires
    a single optimization target: prod, repro, or debug and any number of supplementary targets: openmp and lto
    Append supplementary targets to the primary target using a hyphen separator.

  platform
    The name of the platform from platforms.yaml.
