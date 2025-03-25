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
