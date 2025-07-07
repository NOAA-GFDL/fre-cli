# FRE list
`fre list` provides subtools that help to manage and read yaml files.

## Quickstart
If on gaea or ppan:
```
# Load FRE 
module load fre/[CURRENT FRE VERSION]

# Clone fre-cli repo (to-do: if fre-examples was more robust/updated, we could use that repo for example yaml configurations. For now, we can use fre-cli test examples)
git clone --recursive https://github.com/NOAA-GFDL/fre-cli.git
cd fre-cli 

##########
# make test directories
cd fre/make/tests/null_example

# List post-processing experiments defined in model yaml
fre list exps -y null_model.yaml

# List platforms available in platforms yaml
fre list platforms -y null_model.yaml

##########
# pp test directory
cd ../../../pp/tests/AM5_example/

# List components that will be post-processed
fre list pp-components -y am5.yaml -e c96L65_am5f7b12r1_amip
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

## Tests

To run `fre list` test scripts, return to root directory of the fre-cli repo and call those tests with

    pytest fre/list/tests/[test script.py]

Or run all tests with

    pytest fre/list/tests
