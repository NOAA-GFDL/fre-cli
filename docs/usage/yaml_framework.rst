In order to utilize FRE 2024.01 tools, a distrubuted YAML structure is required. This framework includes a main model yaml, a compile yaml, a platforms yaml, and post-processing yamls. Throughout the compilation and post-processing steps, combined yamls that will be parsed for information are created. Yamls follow a dictionary-like structure with ``[key]: [value]`` fields. 

Yaml Formatting
----------
Helpful information and format recommendations for creating yaml files.

1. You can define a block of values as well as individual ``[key]: [value]`` pairs: 

.. code-block::

  section name:
    key: value
    key: value

2. ``[key]: [value]`` pairs can be made a list by utilizing a ``-``:

.. code-block::

  section name:
    - key: value
    - key: value

3. If you want to associate information with a certain listed element, follow this structure:

.. code-block::

  section name:
    - key: value
      key: value
    - key: value
      key: value

Where each dash indicates a list.

4. Yamls also allow for the capability of reusable variables. These variables are defined by:

.. code-block::

  &ReusableVariable Value

5. Users can apply a reusable variable on a block of values. For example, everything under "section" is associated with the reusable variable:

.. code-block::

  section: &ReusableVariable
    - key: value
      key: value
    - key: value

6. In order to use them as a reference else where in either the same or other yamls, use ``*``:

.. code-block:: 

  *ReusableVariable

7. If the reusable variable must be combined with other strings, the **`!join`** constructor is used. Example: 

.. code-block:: 

  &version "2024.01"
  &stem !join [FRE/, *version]

In this example, the reuasble variable ``stem`` will be parsed as ``FRE/2024.01``.

Model Yaml
----------
The model yaml defines reusable variables, shared directories, switches, post-processing settings, and paths to compile and post-processing yamls. Required fields in the model yaml include: ``fre_properties``, ``build``, ``shared``, and ``experiments``.

* **fre_properties**: Reusable variables

  - list of variables
  - these values can be extracted from ``fre_properties`` in a group's XML, if available
  - value type: string

  .. code-block::

     - &variable1  "value1"  (string)
     - &variable2  "value2"  (string)

* **build**: paths to information needed for compilation

  - subsections: ``compileYaml``, ``platformYaml``
  - value type: string

  .. code-block::

     build:
       compileYaml: "path the compile yaml in relation to model yaml"   (string)
       platformYaml: "path to platforms.yaml in relation to model yaml" (string)

* **shared**: shared settings across experiments

  - subsections: ``directories``, ``postprocess``

  .. code-block::

     shared: 
       directories: &shared_directories
         key: "value"               (string)

       postprocess: 
         settings: &shared_settings
           key: "value"             (string)
         switches: &shared_switches
           key: True/False          (boolean)

  * **Be sure to define directories, settings, and switches as reusable variables as well**

    + they will be "inherited" in the post-processing yamls created

* **experiments**: list of post-processing experiments

  - subsections: ``name``, ``pp``, ``analysis``

  .. code-block::

     experiments:
       - name: name of post-processing experiment                                       (string)
         pp: 
           - path/to/post-processing/yaml for that experiment in relation to model yaml (string)
         analysis: 
           - path/to/analysis/yaml for that experiment in relation to model yaml        (string)

Compile Yaml
----------
The compile yaml defines compilation information including component names, repos, branches, necessary flags, and necessary overrides. This is discussed more in the "Build FMS Model" section.

Platforms Yaml
----------
The platform yaml contains user defined information for both bare-metal and container platforms. Information includes the platform name, the compiler used, necessary modules to load, an mk template, fc, cc, container build, and container run. This yaml file is not model specific. 

  .. code-block::

    platforms:
      - name: the platform name
        compiler: the compiler you are using
        modulesInit: ["array of commands that are needed to load modules." , "each command must end with a newline character"]
        modules: [array of modules to load including compiler]
        fc: the name of the fortran compiler
        cc: the name of the C compiler
        mkTemplate: The location of the mkmf make template
        modelRoot: The root directory of the model (where src, exec, experiments will go)
      - container platform: container platform name
        compiler: compiler you are using
        RUNenv: Commands needed at the beginning of a RUN in dockerfile
        modelRoot: The root directory of the model (where src, exec, experiments will go) INSIDE of the container (/apps)
        fc: name of fortan compiler
        cc: name of C compiler
        container: True if this is a container platform
        containerBuild: "podman" - the container build program
        containerRun: "apptainer" - the container run program


Post-Processing Yaml
----------
The post-processing yamls include information specific to experiments, such as directories to data and other scripts used, switches, and component information. The post-processing yaml can further define more ``fre_properties`` that may be experiment specific. If there are any repeated reusable variables, the ones set in this yaml will overwrite those set in the model yaml. This is discussed further in the "Postprocess FMS History Output" section.
