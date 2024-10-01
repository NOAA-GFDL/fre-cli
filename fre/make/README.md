# **Fremake Canopy**
Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

* Fremake Canopy Supports:
   - multiple targets; use `-t` flag to define each target
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build**

** **Note: Users will not be able to create containers without access to podman**

The fremake canopy fre-cli subcommands are described below ([Subtools](#subtools)), as well as a Guide on the order in which to use them ([Guide](#guide)).

Additionally, as mentioned, multiple targets can be used more multiple target-platform combinations. Below is an example of this usage for both the bare-metal build and container build, using the AM5 model

- [Bare-metal Example](#bare-metal-build) 
- [Bare-metal Multi-target Example](#bare-metal-build-multi-target)  
- [Container Example](#container-build)

## **Usage (Users)**
* Refer to fre-cli [README.md](https://github.com/NOAA-GFDL/fre-cli/blob/main/README.md) for foundational fre-cli usage guide and tips.

## **Quickstart** 
### **Bare-metal Build:**
```bash
# Create checkout script
fre make create-checkout -y am5.yaml -p ncrc5.intel23 -t prod
      
# Create and run checkout script
fre make create-checkout -y am5.yaml -p ncrc5.intel23 -t prod --execute

# Create Makefile
fre make create-makefile -y am5.yaml -p ncrc5.intel23 -t prod

# Create the compile script
fre make create-compile -y am5.yaml -p ncrc5.intel23 -t prod

# Create and run the compile script
fre make create-compile -y am5.yaml -p ncrc5.intel23 -t prod --execute
```
### **Bare-metal Build Multi-target:**
```bash
# Create checkout script
fre make create-checkout -y am5.yaml -p ncrc5.intel23 -t prod -t debug
      
# Create and run checkout script
fre make create-checkout -y am5.yaml -p ncrc5.intel23 -t prod -t debug --execute

# Create Makefile
fre make create-makefile -y am5.yaml -p ncrc5.intel23 -t prod -t debug

# Create the compile script
fre make create-compile -y am5.yaml -p ncrc5.intel23 -t prod -t debug

# Create and run the compile script
fre make create-compile -y am5.yaml -p ncrc5.intel23 -t prod -t debug --execute
```

### **Container Build:**
In order for the container to build successfully, a `-npc`, or `--no-parallel-checkout` is needed.
```bash
# Create checkout script
fre make create-checkout -y am5.yaml -p hpcme.2023 -t prod -npc
      
# Create and run checkout script
fre make create-checkout -y am5.yaml -p hpcme.2023 -t prod -npc --execute

# Create Makefile
fre make create-makefile -y am5.yaml -p hpcme.2023 -t prod

# Create Dockerfile
fre make create-dockerfile -y am5.yaml -p hpcme.2023 -t prod

# Create and run the Dockerfile
fre make create-dockerfile -y am5.yaml -p hpcme.2023 -t prod --execute
```

### **Run all of fremake:**
```bash
# Bare-metal 
fre make run-fremake -y am5.yaml -p ncrc5.intel23 -t prod

# Container
fre make run-fremake -y am5.yaml -p hpcme.2023 -t prod -npc 
```

## Subtools
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
# Create checkout script
fre make create-checkout -y [model yaml file] -p [platform] -t [target]
      
# Create and run checkout script
fre make create-checkout -y [model yaml file] -p [platform] -t [target] --execute

# Create Makefile
fre make create-makefile -y [model yaml file] -p [platform] -t [target]

# Creat the compile script
fre make create-compile -y [model yaml file] -p [platform] -t [target]

# Create and run the compile script
fre make create-compile -y [model yaml file] -p [platform] -t [target] --execute

# Run all of fremake 
fre make run-fremake -y [model yaml file] -p [platform] -t [target] [other options...]
```

### **Container Build:**
For the container build, parallel checkouts are not supported, so the `-npc` options must be used for the checkout script. In addition the platform must be a container platform. 

***To reiterate, users will not be able to create containers unless they have podman access on gaea.***
```bash
# Create checkout script
fre make create-checkout -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] -npc
      
# Create and run checkout script
fre make create-checkout -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute

# Create Makefile
fre make create-makefile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

#Create a Dockerfile
fre make create-dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

# Create and run the Dockerfile
fre make create-dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute
```
