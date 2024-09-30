## FRE yamltools
`fre yamltools` provides subtools that help to manage and perform operations on yaml files. 

## Subtools
- `fre yamltools combine-yamls [options]`
   - Purpose: 
        - Creates combined yaml file in which the [model].yaml, compile.yaml, and platforms.yaml are merged if `--use compile` is specified
        - Creates combined yaml file in which the [model].yaml, [experiment].yaml, and [analysis].yaml are merged if `--use pp` is specified
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-e,  --experiment [experiment name]`
        - `--use [compile|pp] (required)`

### **Tests**

To run `fre yamltools` test scripts, return to root directory of the fre-cli repo and call those tests with

    python -m pytest fre/yamltools/tests/[test script.py]

Or run all tests with

    python -m pytest fre/yamltools/tests
