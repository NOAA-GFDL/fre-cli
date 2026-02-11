============
Glossary
============

.. glossary::
  :sorted:

  target
    The mkmf targets correspond to macros in the template file specified by platforms.yaml. Users must provide a
    single optimization target: either prod, repro, or debug. To enable supplementary features such as openmp or
    lto, append them to the primary target using a hyphen separator.

  platform
    The name of the platform from platforms.yaml.
