## FRE yamltools
`fre yamltools` provides subtools that help to manage and perform operations on yaml files. 

## Quickstart

To access YAML examples, clone the fre-cli repository:

    git clone --recursive https://github.com/NOAA-GFDL/fre-cli.git

    cd fre/yamltools/tests

### Independent subtool use

    fre yamltools combine -y yamls/model.yaml,yamls/compile_yamls/platforms.yaml,yamls/compile_yamls/compile.yaml -o out.yaml

### Piped from `fre list`

    fre list yamls -y yamls/model.yaml | fre -v yamltools combine -o out.yaml

## Subtools
- `fre yamltools combine [options]`
   - Purpose:
        - Creates combined and resolved YAML file using the YAML configurations passed.
        - Input yamls can be passed as standard input from `fre list yamls`
        - Model YAML must be passed first 
   - Options:
        - `-y, --yamls [comma separated string of paths of yamls to combine] `
        - `-e,  --experiment [experiment name]`
        - `-p, --platform [platform]`
        - `-t, --target [target]`
        - `-o, --output [path to output file]`
        - `--no-clean`
