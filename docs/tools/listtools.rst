``exps``
-----------------

``fre list exps [options]``
   - Purpose: List available post-processing experiments included in the yaml configurations
   - Options:
        - ``-y, --yamlfile [experiment yaml]``

``platforms``
-----------------

``fre list platforms [options]``
   - Purpose: List available platforms included in the yaml configurations
   - Options:
        - ``-y, --yamlfile [experiment yaml]``

``pp-components``
-----------------

``fre list pp-components [options]``
   - Purpose: List components in the postprocessing yaml that will be post-processed. All components will be post-processed unless ``postprocess_on: False`` is specified
   - Options:
        - ``-y, --yamlfile [experiment yaml]``
        - ``-e, --experiment [experiment to be post-processed]``
