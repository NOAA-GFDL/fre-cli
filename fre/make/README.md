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
### **Bare-metal Build:**
```bash
# Create checkout script
fre make create-checkout -y [experiment yaml file] -p [platform] -t [target]
      
# Create and run checkout script
fre make create-checkout -y [experiment yaml file] -p [platform] -t [target] -e

# Create Makefile
fre make create-makefile -y [experiment yaml file] -p [platform] -t [target]

# Creat the compile script
fre make create-compile -y [experiment yaml file] -p [platform] -t [target]

# Create and run the compile script
fre make create-compile -y [experiment yaml file] -p [platform] -t [target] -e

# Run all of fremake 
fre make run-fremake -y [experiment yaml] -p [platform] -t [target] [other options...]
```

### **Bare-metal Build (Multi-target example):**
```bash
# Create checkout script
fre make create-checkout -y am5.yaml -p ncrc5.intel -t prod-openmp -t debug
      
# Create and run checkout script
fre make create-checkout -y am5.yaml -p ncrc5.intel -t prod-openmp -t debug -e

# Create Makefile
fre make create-makefile -y am5.yaml -p ncrc5.intel -t prod-openmp -t debug

# Creat the compile script
fre make create-compile -y am5.yaml -p ncrc5.intel -t prod-openmp -t debug

# Create and run the compile script
fre make create-compile -y am5.yaml -p ncrc5.intel -t prod-openmp -t debug -e

# Run all of fremake 
fre make run-fremake -y am5.yaml -p ncrc5.intel -t prod-openmp -t debug [other options...]
```

### **Container Build:**
For the container build, parallel checkouts are not supported, so the `-npc` options must be used for the checkout script. In addition the platform must be a container platform. ***To reiterate, users will not be able to create containers unless they have podman access on gaea.***
```bash
# Create checkout script
fre make create-checkout -y [experiment yaml file] -p [CONTAINER PLATFORM] -t [target] -npc
      
# Create and run checkout script
fre make create-checkout -y [experiment yaml file] -p [CONTAINER PLATFORM] -t [target] -e -npc

# Create Makefile
fre make create-makefile -y [experiment yaml file] -p [CONTAINER PLATFORM] -t [target] 

# Create the compile script
fre make create-compile -y [experiment yaml file] -p [CONTAINER PLATFORM]-t [target] 

#Create a Dockerfile
fre make create-dockerfile -y [experiment yaml file] -p [CONTAINER PLATFORM] -t [target] 

# Create and run the Dockerfile
fre make create-dockerfile -y [experiment yaml file] -p [CONTAINER PLATFORM] -t [target]
```
### **Container Build (Multi-target example):**
```bash
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

