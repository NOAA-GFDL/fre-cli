The model yaml defines reusable variables and paths to compile, post-processing, analysis, and cmor yamls. Required fields in the model yaml include: ``fre_properties``, ``build``,  and ``experiments``.

* `fre_properties`: Reusable variables

  - list of variables
  - these values can be extracted from ``fre_properties`` in a group's XML, if available
  - value type: string

* `build`: paths to information needed for compilation

* `experiments`: list of post-processing experiments

The model.yaml can follow the structure below:

  .. code-block::

     fre_properties: 
       - &variable1  "value1"  (string)
       - &variable2  "value2"  (string)

     build:
       compileYaml: "path the compile yaml in relation to model yaml"    (string)
       platformYaml: "path to platforms.yaml in relation to model yaml"  (string)

     experiments:
       - name: "name of post-processing experiment"                                       (string)
         pp: 
           - "path/to/post-processing/yaml for that experiment in relation to model yaml" (string)
         analysis: 
           - "path/to/analysis/yaml for that experiment in relation to model yaml"        (string)
         cmor:
           - "path/to/cmor/yaml for that experiment in relation to model yaml"            (string)
