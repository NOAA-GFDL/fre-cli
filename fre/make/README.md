# **Fremake Canopy**
Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

* Fremake Canopy Supports:
   - multiple targets; use `-t` flag to define each target
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build**

** **Note: Users will not be able to create containers without access to podman**

## **Usage (Users)**
* Refer to fre-cli [README.md](https://github.com/NOAA-GFDL/fre-cli/blob/main/README.md) for foundational fre-cli usage guide and tips.

## Guide
In order to use the `fre make` tools, remember to create a combined yaml first. This can be done with the `fre yamltools combine-yamls` tool. This combines the model, compile, platform, experiment, and any analysis yamls into ONE yaml file for parsing and validation. 

To combine: 
`fre yamltools combine-yamls -y [model yaml file] -e [experiment name] -p [platform] -t [target]`

### **Bare-metal Build:**
```bash
# Create checkout script
fre make checkout-script -y [model yaml file] -p [platform] -t [target]
      
# Create and run checkout script
fre make checkout-script -y [model yaml file] -p [platform] -t [target] --execute

# Create Makefile
fre make makefile -y [model yaml file] -p [platform] -t [target]

# Create the compile script
fre make compile-script -y [model yaml file] -p [platform] -t [target]

# Create and run the compile script
fre make compile-script -y [model yaml file] -p [platform] -t [target] --execute

# Run all of fremake 
fre make all -y [model yaml file] -p [platform] -t [target] [other options...]
```

### **Container Build:**
For the container build, parallel checkouts are not supported, so the `-npc` options must be used for the checkout script. In addition the platform must be a container platform. 

***To reiterate, users will not be able to create containers unless they have podman access on gaea.***
```bash
# Create checkout script
fre make checkout-script -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] -npc
      
# Create and run checkout script
fre make checkout-script -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute

# Create Makefile
fre make makefile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

#Create a Dockerfile
fre make dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

# Create and run the Dockerfile
fre make dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute
```
