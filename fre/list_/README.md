# FRE list
`fre list` provides subtools that help to manage and read yaml files.

## Quickstart
```
# List post-processing experiments defined in model yaml
fre list exps -y fre/make/tests/null_example/null_model.yaml
```

Example output:
```
[ INFO:list_experiments_script.py:list_experiments_subtool] Experiments found:
[ INFO:list_experiments_script.py:list_experiments_subtool]    - null_model_full
[ INFO:list_experiments_script.py:list_experiments_subtool]    - null_model_0
[ INFO:list_experiments_script.py:list_experiments_subtool]    - null_model_1
[ INFO:list_experiments_script.py:list_experiments_subtool]    - null_model_2
```

```
# List platforms available in platforms yaml
fre list platforms -y fre/make/tests/null_example/null_model.yaml
```

Example output:
```
[ INFO:list_platforms_script.py:  list_platforms_subtool] Platforms available:
[ INFO:list_platforms_script.py:  list_platforms_subtool]     - ncrc5.intel23
[ INFO:list_platforms_script.py:  list_platforms_subtool]     - hpcme.2023
[ INFO:list_platforms_script.py:  list_platforms_subtool]     - ci.gnu
[ INFO:list_platforms_script.py:  list_platforms_subtool]     - hpcmini.2025
[ INFO:list_platforms_script.py:  list_platforms_subtool]     - hpcmini.2025.Specify.Location
[ INFO:list_platforms_script.py:  list_platforms_subtool]     - con.twostep
```


```
# List components that will be post-processed
fre list pp-components -y fre/pp/tests/AM5_example/am5.yaml -e c96L65_am5f7b12r1_amip
```

Example output:
```
[ INFO:list_pp_components_script.py:    list_ppcomps_subtool] Components to be post-processed:
[ INFO:list_pp_components_script.py:    list_ppcomps_subtool]    - atmos_cmip
[ INFO:list_pp_components_script.py:    list_ppcomps_subtool]    - atmos
[ INFO:list_pp_components_script.py:    list_ppcomps_subtool]    - atmos_level_cmip
[ INFO:list_pp_components_script.py:    list_ppcomps_subtool]    - atmos_level
[ INFO:list_pp_components_script.py:    list_ppcomps_subtool]    - atmos_month_aer
[ INFO:list_pp_components_script.py:    list_ppcomps_subtool]    - atmos_diurnal
[ INFO:list_pp_components_script.py:    list_ppcomps_subtool]    - atmos_scalar
```

```
# List yamls to be combined
fre list yamls -y fre/list_/tests/yamls/model.yaml
```

Example output:
```
[ INFO:    list_yamls_script.py:      list_yamls_subtool] YAMLS to be combined (Experiment => None):
[ INFO:    list_yamls_script.py:      list_yamls_subtool]   - /home/Dana.Singh/fre/singh/cli-dev/gen-yaml-ser-2.0/fre/list_/tests/yamls/model.yaml
[ INFO:    list_yamls_script.py:      list_yamls_subtool]   - /home/Dana.Singh/fre/singh/cli-dev/gen-yaml-ser-2.0/fre/list_/tests/yamls/compile.yaml
[ INFO:    list_yamls_script.py:      list_yamls_subtool]   - /home/Dana.Singh/fre/singh/cli-dev/gen-yaml-ser-2.0/fre/list_/tests/yamls/platforms.yaml
[WARNING:    list_yamls_script.py:      list_yamls_subtool] **DNE**: /home/Dana.Singh/fre/singh/cli-dev/gen-yaml-ser-2.0/fre/list_/tests/yamls/compile.yaml
[WARNING:    list_yamls_script.py:      list_yamls_subtool] **DNE**: /home/Dana.Singh/fre/singh/cli-dev/gen-yaml-ser-2.0/fre/list_/tests/yamls/platforms.yaml
```

## Subtools
- `fre list exps [options]`
   - Purpose: Lists the post-processing experiments available from the model yaml
   - Options:
        - `-y, --yamlfile [model yaml] (str; required)`

- `fre list platforms [options]`
   - Purpose: Lists the platforms available from the `platforms.yaml`
   - Options:
        - `-y, --yamlfile [model yaml] (str; required)`

- `fre list pp-components [options]`
   - Purpose: Lists the components to be post-processed
   - Options:
        - `-y, --yamlfile [model yaml] (str; required)`
        - `-e, --experiment [experiment name] (str; required)`

- `fre list yamls [options]`
   - Purpose: Lists the yaml configuration files to be combined; can be associated with an experiment name
   - Options:
        - `-y, --yamlfile [model yaml] (str; required)`
        - `-e, --experiment [experiment name]`
