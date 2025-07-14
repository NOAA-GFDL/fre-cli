# FRE list
`fre list` provides subtools that help to manage and read yaml files.

## Quickstart
```
# List post-processing experiments defined in model yaml
fre list exps -y fre/make/tests/null_example/null_model.yaml

# List platforms available in platforms yaml
fre list platforms -y fre/make/tests/null_example/null_model.yaml

##########
# List components that will be post-processed
fre list pp-components -y fre/pp/tests/AM5_example/am5.yaml -e c96L65_am5f7b12r1_amip
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
