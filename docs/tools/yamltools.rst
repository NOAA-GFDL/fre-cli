``combine-yamls``
-----------------

``fre yamltools combine [options]``
   - Purpose: Creates a fully resolved, combined YAML file. Input yamls can be passed
              as standard input from ``fre list yamls``. The model YAML must be passed
              first.

   - Options:
        - ``-y, --yamls [comma separated string of paths of yamls] ``
        - ``-e,  --experiment [experiment name]``
        - ``-p, --platform [platform]``
        - ``-t, --target [target]``
        - ``-o, --output [path to output file]``
        - ``--no-clean``
