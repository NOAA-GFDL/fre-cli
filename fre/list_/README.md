## FRE list
`fre list` provides subtools that help to manage and read yaml files.

## Subtools
- `fre list exps [options]`
   - Purpose: 
        - Lists the post-processing experiments available from the model yaml
   - Options:
        - `-y, --yamlfile [model yaml] (required)`

- `fre list platforms [options]`
   - Purpose: 
        - Lists the platforms available from the `platforms.yaml`
   - Options:
        - `-y, --yamlfile [model yaml] (required)`

- `fre list pp-components [options]`
   - Purpose: 
        - Lists the post-processing experiments available
   - Options:
        - `-y, --yamlfile [model yaml] (required)`
        - `-e, --experiment [experiment name] (required)`

### **Tests**

To run `fre list` test scripts, return to root directory of the fre-cli repo and call those tests with

    pytest fre/list/tests/[test script.py]

Or run all tests with

    pytest fre/list/tests

