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

## Individual YAML validation

Before combining files, `consolidate_yamls` validates each input using the
convention for its role. This happens at the YAML parser-event level, so an
individual file can be checked before aliases that refer to anchors in another
file are resolved.

| YAML kind | Required top-level keys | Optional top-level keys |
| --- | --- | --- |
| model | `experiments` | `build`, `fre_cli_version`, `fre_properties` |
| compile | `compile` | `fre_properties` |
| platforms | `platforms` | `fre_properties` |
| post-processing | `postprocess` | `fre_properties` |
| analysis | `analysis` | `fre_properties` |
| CMOR | `cmor` | `fre_properties`, `grids` |
| grids | `grids` | `fre_properties` |
| settings | `directories`, `postprocess` | `fre_properties` |

Validation rejects missing or unexpected top-level keys, duplicate top-level
keys, and values with the wrong collection shape. Errors name both the YAML
kind and file that must be corrected.

### **Tests**

To run `fre yamltools` test scripts, return to root directory of the fre-cli repo and call those tests with

    python -m pytest fre/yamltools/tests/[test script.py]

Or run all tests with

    python -m pytest fre/yamltools/tests
