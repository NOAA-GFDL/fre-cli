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
   - Purpose: Lists components to be post-processed in the postprocessing yaml configurations (associated with `postprocess_on: True` or the absence of the key)
   - Options:
        - ``-y, --yamlfile [experiment yaml]``
        - ``-e, --experiment [experiment to be post-processed]``
