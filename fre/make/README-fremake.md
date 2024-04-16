# **Fremake Canopy**

Through the fre-cli, `fre make` can be used to create and run a code checkout script and compile a model.

## **Usage (Users)**

* Refer to fre-cli README.md for foundational fre-cli usage guide and tips.
* Fremake package repository located at: https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy/-/tree/main

### **Subtools Guide**

1)  **fre make**
    - create-checkout
        - Purpose: Creates the checkout script and checks out source code (with execute option)
        - Bare-metal
            - Checkout script supports parallel checkouts
            - Syntax: 
                - To create file: `fre make create-checkout -y [experiment yaml file] -p [platform] -t [target]`
                - To create and run file: `fre make create-checkout -y [experiment yaml file] -p [platform] -t [target] -e`
        - Container 
                - Checkout script is created in a tmpDir location, to eventually be copied into the container via the Dockefile
                - Checkout script does not support parallel checkouts
                - Syntax: 
                    - To create file: `fre make create-checkout -y [experiment yaml file] -p [container platform] -t [target] -npc`
        - Example: `fre pp create-checkout -y am5.yaml -p ncrc5.intel -t prod`
    - create-makefile
        - Purpose: Creates the makefile
        - Bare-metal Syntax: `fre make create-makefile -y [experiment yaml file] -p [platform] -t [target]`
        - Container Syntax: `fre make create-makefile -y [experiment yaml file] -p [container platform] -t [target]`
    - create-compile
        - Purpose: Creates the compile script and compiles the model (with execute option)
        - Bare-metal Syntax:
            - To create file: `fre make create-checkout -y [experiment yaml file] -p [platform] -t [target]`
            - To create and run file: `fre make create-compile -y [experiment yaml file] -p [platform] -t [target] -e``
    - create-dockerfile
        - Purpose: Creates the dockerfile and creates the container (with execute option)
        - With the creation of the dockerfile, the Makefile, checkout script, and any other necessary script is copied into the container from a temporary location
        - Container Syntax:
            - To create file: `fre make create-dockerfile -y [experiment yaml file] -p [container platform] -t [target] -npc`
            - To create and run file: `fre make create-dockerfile -y [experiment yaml file] -p [platform] -t [target] -npc -e``
    - run-fremake
        - Purpose: Create the checkout script, Makefile, compile script, and dockerfile (platform dependent) for the compilation of the model 
        - Syntax:
            - fre make run-fremake -y [experiment yaml] -p [platform] -t [target] [other options...]

