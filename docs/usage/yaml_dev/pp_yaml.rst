The post-processing yamls include information specific to experiments, such as component information. The post-processing yamls can further define more ``fre_properties`` that may be experiment specific. If there are any repeated reusable variables, the ones set in this yaml will overwrite those set in the model yaml.

* **Post-processing yamls**

The post-processing yamls include pp experiment yamls, along with a settings.yaml, that can be applied to all pp yamls. Users can add however many components are needed, as well as define any experiment specific `fre_properties`. The pp experiment yamls can follow the structure below:

.. code-block:: 

   postprocess:
     components:
       - type: "component name"                                                          (string)
         sources:
           - history_file: "history file to include with component"                      (string)
             variables: "specific variables to postprocess associated with component"    (array with string elements)
         xyInterp: "lat, lon grid configuration"                                         (string)
         interpMethod: "interpolation method"                                            (string)
         sourceGrid: "input grid type"                                                   (string)
         inputRealm: "domain of component"                                               (string)
         static:
           - source: "static history file to include with component"                     (string)
             variables: "specific static variables to postprocess"                       (array with string elements)
           - offline_diagnostic: "path to static offline diagnostic"                     (string)
             variables: "specific static variables to postprocess"                       (array with string elements)
         postprocess_on: "switch to postprocess this component or not"                   (boolean)

Out of the keys listed above, required keys include:
    
    - type
    - sources
    - postprocess_on

* **Setting yaml**

To define post-processing settings, a settings.yaml must also be created. This configuration file will include post-processing settings and switches and will be listed as the first yaml under the `pp` section of `experiments`.

This file can follow the format below:

.. code-block:: 

   directories:
     history_dir:
     pp_dir:
     analysis_dir:
     ptmp_dir:

   postprocess:
     settings:
       site: "site name from file that defines parameters that can be specific to where the workflow is being run"        (string)
       history_segment: "amount of time covered by a single history file (ISO8601 datetime)"                              (string)
       pp_start: "start of the desired postprocessing (ISO8601 datetime)"                                                 (string)
       pp_stop: "end of the desired postprocessing (ISO8601 datetime)"                                                    (string)
       pp_chunk_a: "amount of time covered by a single postprocessed file (ISO8601 datetime)"                             (string)
       pp_chunk_b: "secondary chunk size for postprocessed files, if desired (ISO8601 datetime). Divisble by pp_chunk_a"  (string)
       pp_grid_spec: "path to FMS grid definition tarfile"                                                                (string)
     switches:
       do_timeavgs: "switch to turn on/off time-average file generation"                                                  (boolean)
       clean_work: "switch to remove intermediate data files when they are no longer needed"                              (boolean)
       do_refinediag: "switch to run refine-diag script(s) on history file to generate additional diagnostics"            (boolean)
       do_atmos_plevel_masking: "switch to mask atmos pressure-level output above/below surface pressure/atmos top"       (boolean)
       do_preanalysis: "switch to run a pre-analysis script on history files"                                             (boolean)
       do_analysis: "switch to launch analysis scripts"                                                                   (boolean)
       do_analysis_only: "switch to only launch analysis scripts"                                                         (boolean)

Required keys include:

    - history_dir
    - pp_dir
    - ptmp_dir
    - site
    - history_segment
    - pp_chunk_a
    - pp_start
    - pp_stop
    - pp_grid_spec
    - clean_work
    - do_timeavgs
    - do_refinediag
    - do_atmos_plevel_masking
    - do_preanalysis
    - do_analysis
    - do_analysis_only
