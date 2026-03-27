# **Fre make**
Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

* Fre make Supports:
   - multiple targets; use `-t` flag to define each target
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build**

**Note: Users will not be able to create containers without access to podman**

## Quickstart

The quickstart instructions can be used with the null model example located in the fre-cli repository: https://github.com/NOAA-GFDL/fre-cli/tree/main/fre/make/tests/null_example

Users can clone the fre-cli repository and invoke the commands below from the root of the repository. 
### Bare-metal Build:

```bash
# Create and run checkout script: checkout script will check out source code as defined in the compile.yaml
fre make checkout-script -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod --execute

# Create Makefile
fre make makefile -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod

# Create and run the compile script to generate a model executable
fre make compile-script -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod --execute
```
### Bare-metal Build (Multi-target):

```bash
# Create and run checkout script: checkout script will check out source code as defined in the compile.yaml
fre make checkout-script -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

# Create Makefile
fre make makefile -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod -t debug

# Create and run a compile script for each target specified; generates model executables
fre make compile-script -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute
```

### Container Build:
In order for the container to build successfully, the parallel checkout feature is disabled.

```bash
# Create checkout script
fre make checkout-script -y fre/make/tests/null_example/null_model.yaml -p hpcme.2023 -t prod

# Create Makefile
fre make makefile -y fre/make/tests/null_example/null_model.yaml -p hpcme.2023 -t prod

# Create the Dockerfile and container build script: the container build script (createContainer.sh) uses the Dockerfile to build a model container
fre make dockerfile -y fre/make/tests/null_example/null_model.yaml -p hpcme.2023 -t prod --execute
```

### Run all of fremake:

`all` kicks off the compilation automatically

```bash
# Bare-metal: create and run checkout script, create makefile, create and RUN compile script to generate a model executable
fre make all -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod --execute

# Container: create checkout script, makefile, create dockerfile, and create and RUN the container build script to generate a model container
fre make all -y fre/make/tests/null_example/null_model.yaml -p hpcme.2023 -t prod --execute
```

## Subtools
- `fre make checkout-script [options]`
   - Purpose: 
   - Options:
        - `-y, --yamlfile [model yaml] (str; required)`
        - `-p, --platform`
        - `-t, --target`
        - `-gj, --gitjobs`
        - `-npc, --no-parallel-checkout`
        - `--execute`
        - `--force-checkout`
- `fre make makefile [options]`
   - Purpose: 
   - Options:
- `fre make compile-script [options]`
   - Purpose: 
   - Options:
- `fre make dockerfile [options]`
   - Purpose: 
   - Options:
- `fre make all [options]`
   - Purpose: 
   - Options:
