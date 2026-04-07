# **Fre make**
Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

* Fre make Supports:
   - multiple targets; use `-t` flag to define each target
   - multiple platforms; use `-p` flag to define each platform
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build

**Note: The container engine used to create the container (such as podman or docker) is specified in the `platforms.yaml` with the `containerBuild` key. Please ensure the container engine is acccesible before running fre make.**

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
