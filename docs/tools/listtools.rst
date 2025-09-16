``exps``
-----------------

``fre list exps [options]``
   - Purpose: Lists available post-processing experiments included in the yaml configurations
   - Options:
        - ``-y, --yamlfile [experiment yaml]``

``platforms``
-----------------

``fre list platforms [options]``
   - Purpose: Lists available platforms included in the yaml configurations
   - Options:
        - ``-y, --yamlfile [experiment yaml]``

``pp-components``
-----------------

``fre list pp-components [options]``
   - Purpose: Lists components that have the `postprocess_on` key set to `True` in the postprocessing yaml configurations
   - Options:
        - ``-y, --yamlfile [experiment yaml]``
        - ``-e, --experiment [experiment to be post-processed]``
