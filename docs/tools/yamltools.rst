``combine-yamls``
-----------------

``fre yamltools combine-yamls [options]``
   - Purpose: Creates a combined yaml file for either compilation or post-processing. 
              If `--use compile`, the model yaml is combined with the compile and platforms yaml.
              If `--use pp`, the model yaml is combined with post-processing yamls.
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-e, --experiment [experiment name]`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `--use [compile|pp] (required)`
