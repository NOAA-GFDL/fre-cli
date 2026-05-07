# **Fre make**
Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

* Fre make Supports:
   - multiple targets; use `-t` flag to define each target
   - multiple platforms; use `-p` flag to define each platform
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build

**Note: The container engine used to create the container (such as podman or docker) is specified in the `platforms.yaml` with the `containerBuild` key. Please ensure the container engine is acccesible before running fre make.**

## Getting Started

The quickstart instructions [here](https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#quickstart), will build the null model using YAML configurations located in the fre-cli repository. These configurations are combined to create a resolved dictionary that will then be parsed for information to:

1. Create and run a checkout script (using source code for the `FMS`, `ice_param`, and `coupler` components defined in the `compile.yaml`)
2. Create a Makefile
3. Create and run either a compile.sh (for bare-metal builds) or a Dockerfile and createContainer.sh (for container builds)

## Subtools
- `fre make checkout-script [options]`
   - Purpose: Create and run a checkout script. 
   - Options:
        - `-y, --yamlfile [model yaml] (required)`
        - `-p, --platform [platform]   (required)`
        - `-t, --target [target]       (required)`
        - `-gj, --gitjobs`
        - `-npc, --no-parallel-checkout`
        - `--execute`
        - `--force-checkout`

- `fre make makefile [options]`
   - Purpose: Create a Makefile.
   - Options:
        - `-y, --yamlfile [model yaml] (required)`
        - `-p, --platform [platform]   (required)`
        - `-t, --target [target]       (required)`

- `fre make compile-script [options]`
   - Purpose: Create and run a compile script to generate a model executable.
   - Options:
        - `-y, --yamlfile [model yaml] (required)`
        - `-p, --platform [platform]   (required)`
        - `-t, --target [target]       (required)`
        - `-n --nparallel`
        - `-mj --makejobs`
        - `-e, --execute`
        - `-v, --verbose`

- `fre make dockerfile [options]`
   - Purpose: Create and run a Dockerfile to generate a model container.
   - Options:
        - `-y, --yamlfile [model yaml] (required)`
        - `-p, --platform [platform]   (required)`
        - `-t, --target [target]       (required)`
        - `-nft, --no-format-transfer`
        - `-e, --execute`

- `fre make all [options]`
   - Purpose: 
        - For a bare-metal build: Create a checkout script, Makefile, and compile script to generate a model executable
        - For a container build: Create a checkout script, Makefile, and Dockerfile to generate a model container.
   - Options:
        - `-y, --yamlfile [model yaml] (required)`
        - `-p, --platform [platform]   (required)`
        - `-t, --target [target]       (required)`
        - `-n --nparallel`
        - `-mj --makejobs`
        - `gj, --gitjobs`
        - `-npc, --no-parallel-checkout`
        - `-nft, --no-format-transfer`
        - `-e, --execute`
        - `-v, --verbose`
