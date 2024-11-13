``fre make`` can compile a traditional "bare metal" executable or a containerized executable using a set of YAML configuration files.

Through the fre-cli, ``fre make`` can be used to create and run a checkout script, makefile, and compile a model.

Fremake Canopy Supports:
  - multiple targets; use ``-t`` flag to define each target
  - bare-metal build
  - container creation
  - parallel checkouts for bare-metal build

**Note: Users will not be able to create containers without access to podman. To get access, submit a helpdesk ticket.**

Required configuration files:

  - Model Yaml
  - Compile Yaml
  - Platforms yaml

These yamls are combined and further parsed through the ``fre make`` tools.

To create the compile yaml, reference the compile section on an XML. Certain fields should be included under "compile". These include ``experiment``, ``container_addlibs``, ``baremetal_linkerflags``, and ``src``. 

  - The experiment can be explicitly defined or can be used in conjunction with defined ``fre_properties`` from the model yaml, as seen in the code block below
  - ``container_addlibs``: list of strings of packages needed for the model to compile (used to create the link line in the Makefile)
  - ``baremetal_linkerflags``: list of strings of linker flags (used to populate the link line in the Makefile
  - ``src``: contains information about components needed for model compilation

.. code-block:: 

   compile: 
     experiment: !join [*group_version, "_compile"]
     container_addlibs: "libraries and packages needed for linking in container" (string)
     baremetal_linkerflags: "linker flags of libraries and packages needed"      (string)
     src:

The ``src`` section is used to include component information. This will include: ``component``, ``repo``, ``cpdefs``, ``branch``, ``paths``,  ``otherFlags``, and ``makeOverrides``.

.. code-block::
   
   src:
     - component: "component name"                                         (string)
       requires: ["list of components that this component depends on"]     (list of string)
       repo: "url of code repository"                                      (string)
       branch: "version of code to clone"                                  (string / list of strings)
       paths: ["paths in the component to compile"]                        (list of strings)
       cppdefs: "CPPDEFS ot include in compiling componenet                (string)
       makeOverrides: "overrides openmp target for MOM6"                   ('OPENMP=""') (string)
       otherFlags: "Include flags needed to retrieve other necessary code" (string)
       doF90Cpp: True if the preprocessor needs to be run                  (boolean) 

Guide and quickstart to ``fre make`` subtools:
:ref:`fre-make-guide`
