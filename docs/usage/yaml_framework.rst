In order to utilize these FRE tools, a distrubuted YAML structure is required. This framework includes a main model yaml, a compile yaml, a platforms yaml, and post-processing yamls. Throughout the compilation and post-processing steps, combined yamls that will be parsed for information are created. Yamls follow a dictionary-like structure with ``[key]: [value]`` fields. 

.. include:: yaml_dev/yaml_formatting.rst

.. include:: yaml_dev/model_yaml.rst

.. include:: yaml_dev/compile_yaml.rst

.. include:: yaml_dev/platforms_yaml.rst

.. include:: yaml_dev/pp_yaml.rst
