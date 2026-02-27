============
Glossary
============

.. glossary::
  :sorted:

  target
    The term refers to compiler flags to turn on during compilation. `fre-cli` requires a single optimization target:
    `prod`, `repro`, or `debug` and any number of supplementary targets: `openmp` and `lto`. Append supplementary targets to
    the primary target using a hyphen separator. e.g. `repro-openmp`, `prod-openmp-lto`

  platform
    The term refers to the system and compiler that the model is compiled and running on. The platform name is mapped
    to information defined in the platforms.yaml file. This information includes site-specific compilers, directories,
    and setup. e.g. `ncrc5.intel25`
