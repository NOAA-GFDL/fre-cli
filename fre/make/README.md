# **Fre make**
Through the fre-cli, `fre make` can be used to create and run a checkout script, makefile, and compile a model.

* Fre make Supports:
   - multiple targets; use `-t` flag to define each target
   - bare-metal build
   - container creation
   - parallel checkouts for bare-metal build**

** **Note: Users will not be able to create containers without access to podman**

## Guide

### **Bare-metal Build:**
```bash
# Create and run checkout script
fre make checkout-script -y [model yaml file] -p [platform] -t [target] --execute

# Create Makefile
fre make makefile -y [model yaml file] -p [platform] -t [target]

# Create and run the compile script
fre make compile-script -y [model yaml file] -p [platform] -t [target] --execute

# Run fre make checkout-script, fre make makefile, and fre make compile-script in order
fre make all -y [model yaml file] -p [platform] -t [target] [other options...]
```

### **Container Build:**
***To reiterate, users will not be able to create containers unless they have podman access on gaea.***
```bash
# Create and run checkout script
fre make checkout-script -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute

# Create Makefile
fre make makefile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target]

# Create and run the Dockerfile
fre make dockerfile -y [model yaml file] -p [CONTAINER PLATFORM] -t [target] --execute
```
