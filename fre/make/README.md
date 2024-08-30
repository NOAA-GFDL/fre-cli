# **Fremake Canopy**
Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

* Fremake Canopy Supports:
   - multiple targets, would have to use one `-t` flag for each one
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build**

* **Note: Users will not be able to create containers without access to podman**

The fremake canopy fre-cli subcommands are described below ([Subcommands](#subcommands)), as well as a Guide on the order in which to use them ([Guide](#guide)).

Additionally, as mentioned, multiple targets can be used more multiple target-platform combinations. Below is an example of this usage for both the bare-metal build and container build, using the AM5 model

- [Bare-metal Example](#bare-metal-build-multi-target-example)  
- [Container Example](#container-build-multi-target-example)

## **Usage (Users)**
* Refer to fre-cli [README.md](https://github.com/NOAA-GFDL/fre-cli/blob/main/README.md) for foundational fre-cli usage guide and tips.
* Fremake package repository located at: https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy/-/tree/main


## Subcommands
- `fre make create-checkout [options]`
   - Purpose: Creates the checkout script and can check out source code (with execute option)
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-j, --jobs [number of jobs to run simultneously]`
        - `-npc, --no-parallel-checkout (for container build)` 
        - `-e, --execute` 

- `fre make create-makefile [options]`
   - Purpose: Creates the makefile
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`

- `fre make create-compile [options]`
   - Purpose: Creates the compile script and compiles the model (with execute option)
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-j, --jobs [number of jobs to run simultneously]`
        - `-n, --parallel [number of concurrent modile compiles]`
        - `-e, --execute` 

- `fre make create-dockerfile [options]`
   - Purpose: Creates the dockerfile and creates the container (with execute option)
   - With the creation of the dockerfile, the Makefile, checkout script, and any other necessary script is copied into the container from a temporary location
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-e, --execute`

- `fre make run-fremake [options]`
   - Purpose: Create the checkout script, Makefile, compile script, and dockerfile (platform dependent) for the compilation of the model
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-npc, --no-parallel-checkout (for container build)` 
        - `-j, --jobs [number of jobs to run simultneously]`
        - `-n, --parallel [number of concurrent modile compiles]`

## Guide
In order to use the `fre make` tools, remember to create a combined yaml first. This can be done with the `fre yamltools combine-yamls` tool. This combines the model, compile, platform, experiment, and any analysis yamls into ONE yaml file for parsing and validation. 

To combine: 
`fre yamltools combine-yamls -y [model yaml file] -e [experiment name] -p [platform] -t [target]`

### **Bare-metal Build:**
```bash
## NOTE: Remember to create the combined yaml first!
##       The targets used in fremake are taken from the fre make command itself
# Create combined yaml
fre yamltools combine-yamls -y [model yaml file] -e [experiment name] -p [platform] -t [target]

# Create checkout script
fre make create-checkout -y [combined yaml file] -e [experiment name] -p [platform] -t [target]
      
# Create and run checkout script
fre make create-checkout -y [combined yaml file] -e [experiment name] -p [platform] -t [target] --execute

# Create Makefile
fre make create-makefile -y [combined yaml file] -e [experiment name] -p [platform] -t [target]

# Creat the compile script
fre make create-compile -y [combined yaml file] -e [experiment name] -p [platform] -t [target]

# Create and run the compile script
fre make create-compile -y [combined yaml file] -e [experiment name] -p [platform] -t [target] --execute

# Run all of fremake 
fre make run-fremake -y [combined yaml] -e [experiment name] -p [platform] -t [target] [other options...]
```

### **Bare-metal Build (Multi-target example):**
```bash
## NOTE: Remember to create the combined yaml first!
##       The targets used in fremake are taken from the fre make command itself 
# Create combined yaml
fre yamltools combine-yamls -y am5.yaml -e c96L65_am5f7b12r1_amip -p ncrc5.intel23 -t debug 

# Create checkout script
fre make create-checkout -y combined-c96L65_am5f7b12r1_amip.yaml -e c96L65_am5f7b12r1_amip -p ncrc5.intel23 -t prod-openmp -t debug
      
# Create and run checkout script
fre make create-checkout -y combined-c96L65_am5f7b12r1_amip.yaml -e c96L65_am5f7b12r1_amip -p ncrc5.intel23 -t prod-openmp -t debug --execute

# Create Makefile
fre make create-makefile -y combined-c96L65_am5f7b12r1_amip.yaml -e c96L65_am5f7b12r1_amip -p ncrc5.intel23 -t prod-openmp -t debug

# Creat the compile script
fre make create-compile -y combined-c96L65_am5f7b12r1_amip.yaml -e c96L65_am5f7b12r1_amip -p ncrc5.intel23 -t prod-openmp -t debug

# Create and run the compile script
fre make create-compile -y combined-c96L65_am5f7b12r1_amip.yaml -e c96L65_am5f7b12r1_amip -p ncrc5.intel23 -t prod-openmp -t debug --execute

# Run all of fremake 
fre make run-fremake -y combined-c96L65_am5f7b12r1_amip.yaml -e c96L65_am5f7b12r1_amip -p ncrc5.intel23 -t prod-openmp -t debug
```

### **Container Build:**
For the container build, parallel checkouts are not supported, so the `-npc` options must be used for the checkout script. In addition the platform must be a container platform. ***To reiterate, users will not be able to create containers unless they have podman access on gaea.***
```bash
## NOTE: Remember to create the combined yaml first!
##       The targets used in fremake are taken from the fre make command itself
# Create combined yaml
fre yamltools combine-yamls -y [model yaml] -e [experiment name] -p [CONTAINER PLATFORM] -t [target]

# Create checkout script
fre make create-checkout -y [combined yaml file] -e [experiment name] -p [CONTAINER PLATFORM] -t [target] -npc
      
# Create and run checkout script
fre make create-checkout -y [combined yaml file] -e [experiment name] -p [CONTAINER PLATFORM] -t [target] --execute -npc

# Create Makefile
fre make create-makefile -y [combined yaml file] -e [experiment name] -p [CONTAINER PLATFORM] -t [target] 

# Create the compile script
fre make create-compile -y [combined yaml file] -e [experiment name] -p [CONTAINER PLATFORM]-t [target] 

# Create and run the compile script
fre make create-compile -y [combined yaml file] -e [experiment name] -p [CONTAINER PLATFORM]-t [target] --execute

#Create a Dockerfile
fre make create-dockerfile -y [combined yaml file] -e [experiment name] -p [CONTAINER PLATFORM] -t [target] 

# Create and run the Dockerfile
fre make create-dockerfile -y [combined yaml file] -e [experiment name] -p [CONTAINER PLATFORM] -t [target] --execute
```
### **Container Build (Multi-target example):**
```bash
# NOTE: multi-target will be taken from fre make commands
# Create combined yaml
fre yamltools combine-yamls -y am5.yaml -e c96L65_am5f7b12r1_amip -p hpcme.2023 -t debug

# Create checkout script
fre make create-checkout -y am5.yaml -p hpcme.2023 -t prod-openmp -t debug -npc
      
# Create and run checkout script
fre make create-checkout -y am5.yaml -p hpcme.2023 -t prod-openmp -t debug -npc -e

# Create Makefile
fre make create-makefile -y am5.yaml -p hpcme.2023 -t prod-openmp -t debug

# Creat the compile script
fre make create-compile -y am5.yaml -p hpcme.2023 -t prod-openmp -t debug

# Create and run the compile script
fre make create-compile -y am5.yaml -p hpcme.2023 -t prod-openmp -t debug -e

# Run all of fremake 
fre make run-fremake -y am5.yaml -p hpcme.2023 -t prod-openmp -t debug [other options...] -npc 
```
