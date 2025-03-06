# FREMAKE CANOPY
The fremake canopy prototype embodies the checking out of source code and compilation of the model. This rewrite was developed with the idea of portability and flexibilty in mind. 

Fremake canopy is written in python and can support:
- Bare-metal and container builds (with container platform)
    - bare-metal build: 
        - supports parallel checkouts (default behavior)
        - supports parallel model builds
    - container: 
        - e4s container with spack stack package list
- Multiple platforms and targets can be given (for multiple platform-target combinations)
- One yaml format
- Additional library support if needed by model 

Fremake has also been integrated as a fre-cli tool, creating a more modular and interactive experience.

## Get Started
Steps for how to build an example with the AM5 model, for both the bare-metal compilation and container, are outlined below. 

- ### [Set-up environment](#how-to-get-started)
    - Fremake tools are provided through the fre-cli
    - For more information on the fre-cli, see its associated github page: https://github.com/NOAA-GFDL/fre-cli 
- ### [Bare-metal build](#how-to-build-the-bare-metal-example)
    - Note: make sure to have the correct experiment yaml, compile yaml, and platform yaml available for the model compilation
- ### [Container build](#how-to-build-the-container-example)
    - Note: make sure to have the correct experiment yaml, compile yaml and platform yaml available for the model compilation
- ### [Full fremake: bare-metal and container](#how-to-run-complete-fremake) 
    - this can be done for either bare-metal or container builds
    - this tool is available to give the option to run fremake fully, not in steps


## YAMLS:
experiment yaml: This is the main yaml and gives the path to the other yamls
```yaml
platformYaml: path to yaml containing the platforms
layoutYaml: path to the yaml containing the layouts (not used currently)
compileYaml: path to the yaml with the model source code and build information
experiments: path to the yaml that has information about expeiment configurations (not currently used)

```

compile yaml: Containers information about source code and how to build
```yaml
experiment: name of the model
container_addlibs: ["comma separated list of additional packages/libraries"]
baremetal_linkerflags: ["comma separated list of linker flags needed for each additional package/library"]
src: 
     - component: The name of the component model
       requires: [Array of required components]
       repo: scalar URL of the repo --OR-- [array of URLs to the code repos if more than one is required]
       branch: scalar (or array of same size of repo) of the version of the code to clone
       doF90Cpp: True if the F90cpp needs to be done (land)
       cppdefs: a single string containing all CPPDEFs to add during compilations
       paths: [array of paths to build]
       otherFlags: Additional flags defined as environment variables in the experiment.yaml
```

platform yaml: User defined platform specifications.  This will require more user input that bronx
```yaml
platforms:
   - name: the platform name
     compiler: the compiler you are using
     modulesInit: ["array of commands that are needed to load modules." , "each command must end with a newline character"]
     modules: [array of modules to load including compiler]
     fc: the name of the fortran compiler
     cc: the name of the C compiler
     mkTemplate: The location of the mkmf make template
     modelRoot: The root directory of the model (where src, exec, experiments will go)
     container: True if this is a container platform
     containerBuild: "podman" - the container build program
     containerRun: "apptainer" - the container run program
```

## How to Get started
Set up the environment:
```bash
# Load the fre-cli (if on gaea or somewhere where the fre-cli is available)
module load fre/canopy

# If the fre-cli is not available, follow steps in the fre-cli repository to either create your own conda environment with the fre-cli or activate the fre-cli environment available
# If no fre-cli env available:
conda create -n fremake-env                 # create environment
conda config --append channels noaa-gfdl    # append necessary channels
conda config --append channels conda-forge  # append necessary channels
conda activate fremake-env                  # activate environment 
conda install noaa-gfdl::fre-cli            # install the fre-cli
```

### How to build the Bare-metal example
```bash
# Have access to yamls
# older versino: git clone -b 2023.00 https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy.git

git clone https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy.git
cd fremake_canopy/yamls

# Create and run checkout
# `-e` will run the checkout script after creating it
# without `-e`, the checkout script will just be created
fre make create-checkout -y am5.yaml -p ncrc5.intel -t prod -e 

# Create the Makefile
fre make create-makefile -y am5.yaml -p ncrc5.intel -t prod 

# Create and run the compile script
# `-e` will run the compile script after creating it
# without `-e`, the compile script will just be created
fre make create-compile -y am5.yaml -p ncrc5.intel -t prod -e 
```
*Corresponding files, such as the checkout script, makefile, compile script, and experiment executable will be in the `/exec` folder created in `$HOME/$USER/fremake-canopy/am5/ncrc5.intel-prod/test`*

### How to build the Container example
```bash
# Have access to yamls
# older version: git clone -b 2023.00 https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy.git 

git clone https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy.git
cd fremake_canopy/yamls

# Create and run checkout
# `-e` will run the checkout script after creating it
# without `-e`, the checkout script will just be created
# Be sure to specify `-npc` for non-parallel checkout
fre make create-checkout -y am5.yaml -p hpcme.2023 -t prod -npc -e 

# Create the Makefile
fre make create-makefile -y am5.yaml -p hpcme.2023 -t prod 

# Create and run the dockerfile
# `-e` will run the dockerfile after creating it, to build a container
# without `-e`, the dockerfile will just be created
fre make create-dockerfile -y am5.yaml -p hpcme.2023 -t prod -e 
```
*Corresponding files, such as the checkout script and makefile, will be in a tmp location and copied into the container via the dockerfile. The dockerfile,, as well as the container sif file, will be created in the users current location (yaml folder).*

### How to run complete fremake 
```bash
# Have access to yamls
# older version: git clone -b 2023.00 https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy.git 

git clone https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy.git 
cd fremake_canopy/yamls

# Run fremake
# Can run fremake for bare-metal or container; be sure to give the correct platform for your build
fre make run-fremake -y am5.yaml -p [ncrc5.intel OR hpcme.2023] -t prod 
```
