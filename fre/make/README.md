# **Fre make**
Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

* Fre make Supports:
   - multiple targets; use `-t` flag to define each target
   - multiple platforms; use `-p` flag to define each platform
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build

**Note: The container engine used to create the container (such as podman or docker) is specified in the `platforms.yaml` with the `containerBuild` key. Please ensure the container engine is acccesible before running fre make.**

For a more comprehensive guide to fre make functionality, see [here](----------------------------).

## Quickstart

The quickstart instructions build the null model by loading the FRE module on Gaea C5, and using yaml files located in the fre-cli repository.

To access the null_model configuration, clone the fre-cli repository:

.. code-block::

    git clone --recursive https://github.com/NOAA-GFDL/fre-cli.git

    cd fre/make/tests/null_example

1. All-in-one fre make subtool:

`all` kicks off the compilation automatically

.. code-block::

    # Bare-metal: create and run checkout script, create makefile, create and RUN compile script to generate a model executable
    fre make all -y null_model.yaml -p ncrc5.intel23 -t prod --execute

    # Container: create checkout script, makefile, create dockerfile, and create and RUN the container build script to generate a model container
    fre make all -y null_model.yaml -p hpcme.intel25 -t prod --execute

2. Bare-metal Build with individual subtools (Single target)

For the bare-metal build, the parallel checkout feature is the default behavior.

.. code-block::

  # Create and run checkout script
  fre make checkout-script -y null_model.yaml -p ncrc5.intel23 -t prod --execute

  # Create the Makefile
  fre make makefile -y null_model.yaml -p ncrc5.intel23 -t prod

  # Create and run the compile script
  fre make compile-script -y null_model.yaml -p ncrc5.intel23 -t prod --execute

3. Bare-metal Build with individual subtools (Multiple targets):

.. code-block::

    # Create and run checkout script
    fre make checkout-script -y null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

    # Create the Makefile
    fre make makefile -y null_model.yaml -p ncrc5.intel23 -t prod -t debug

    # Create and run a compile script for each target specified
    fre make compile-script -y null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

4. Container Build with individual subtools:

In order for the container to build successfully, the parallel checkout feature is disabled.

.. code-block::

    # Create checkout script
    fre make checkout-script -y null_model.yaml -p hpcme.intel25 -t prod

    # Create the Makefile
    fre make makefile -y null_model.yaml -p hpcme.intel25 -t prod

    # Create the Dockerfile and container build script
    fre make dockerfile -y null_model.yaml -p hpcme.intel25 -t prod --execute

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
