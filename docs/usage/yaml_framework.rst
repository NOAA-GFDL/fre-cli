In order to utilize FRE Canopy tools, a distrubuted YAML structure is required. This framework includes a main model yaml, a compile yaml, a platforms yaml, and post-processing yamls. Throughout the compilation and post-processing steps, combined yamls that will be parsed for information are created. Yamls follow a dictionary-like structure with `[key]: [value]` fields. 

Helpful information and format recommendations for creating yaml files.
1. You can define a block of values as well as individual `[key]: [value]` pairs: 
```
section name:
  key: value
  key: value
```

2. `[key]: [value]` pairs can be made a list by utilizing a `-`:
```
section name:
  - key: value
  - key: value
```

3. If you want to associate information with a certain listed element, follow this structure:
```
section name:
  - key: value
    key: value
  - key: value
    key: value
```
Where each `-` indicates a different list.

4. Yamls also allow for the capability of reusable variables. These variables are defined by:
`&ReusableVariable Value`

5. Users can apply a reuable variable on a block of values as well. Everything under that section can be included in the reusable variable.
```
section: &ReusableVariable
  - key: value
  - key: value
```

6. In order to use them as a reference else where in either the same or other yamls, follow:
`*ReusableVariable`

7. If the reusable variable must be combined with other strings, the `!join` constructor is used. Example:
```
&version "2024"
&stem !join [FRE/, *version]
```

Model Yaml
----------
The model yaml defines reusable variables, shared directories, switches, and post-processing settings, and paths to compile and post-processing yamls. Required fields in the model yaml include: `fre_properties`, `build`, `shared`, and `experiments`.

* `fre_properties`: Reusable variables
  - list
  - value type: string
  .. code-block::
     - &variable1  "value1"
     - &variable2  "value2"
* `build`: paths to information needed for compilation
  - subsections: `compileYaml`, `platformYaml`
  - value type: string
  .. code-block::
     compileYaml: path the compile yaml in relation to model yaml
     platformYaml: path to platforms.yaml in relation to model yaml
* `shared`: shared settings across experiments
  - subsections: `directories`, `postprocess`
  .. code-block::
     directories: &shared_directories
       key: value (string)
     postprocess: 
       settings: &shared_settings
         key: value (string)
       switches: &shared_switches
         key: value (boolean)
* `experiments`: list of post-processing experiments
  .. code-block::
     - name: name of post-processing experiment (string)
       pp: 
         - path to post-processing yaml for that experiment in relation to model yaml (string)
       analysis: 
         - path to analysis yaml for that experiment in relation to model yaml (string)

*Be sure to define directories, settings, and switches as reusable variables as well; they will be "inherited" in the post-processing yamls created.*

Compile Yaml
----------
The compile yaml defines compilation information including copmonent names, repos, branches, necessary flags, and necessary overrides. In order to create the compile yaml, one can refer to compile information defined in an XML.

Platform Yaml
----------
The platform yaml defines information for both bare-metal and container platforms. Information includes the platform name, the compiler used, necessary modules to load, an mk template, fc, cc, container build, and container run.

Post-Processing Yaml
----------
The post-processing yamls include information specific to experiments, such as directories to data and other scripts used, switches, and component information. The post-processing yaml can further define more `fre_properties` that may be experiment specific. If there are any repeated reuable variables, the ones set in this yaml will overwrite those set in the model yaml. 
