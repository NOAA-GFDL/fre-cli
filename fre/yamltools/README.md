## FRE yamltools
`fre yamltools` provides subtools that help to manage and perform operations on yaml files. 

## Quickstart

To access YAML examples, clone the fre-cli repository:

    git clone --recursive https://github.com/NOAA-GFDL/fre-cli.git

    cd fre/yamltools/tests

### Independent subtool use

    fre yamltools combine -y "yamls/model.yaml,yamls/compile_yamls/platforms.yaml,yamls/compile_yamls/compile.yaml" -o out.yaml

### Piped from `fre list`

    fre list yamls -y yamls/model.yaml | fre -v yamltools combine -o out.yaml

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

- `fre yamltools combine [options]`
   - Purpose:
        - Creates combined and resolved YAML file using the YAML configurations passed.
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-e,  --experiment [experiment name]`
        - `-p, --platform [platform]`
        - `-t, --target [target]`
        - `-o, --output [path to output file]`
