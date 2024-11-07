``create-checkout``
-------------

`fre make create-checkout [options]`
   - Purpose: Creates the checkout script and can check out source code (with execute option)
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-j, --jobs [number of jobs to run simultneously]`
        - `-npc, --no-parallel-checkout (for container build)`
        - `-e, --execute`

``create-makefile`` 
-------------

`fre make create-makefile [options]`
   - Purpose: Creates the makefile
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`

``create-compile``
-------------

`fre make create-compile [options]`
   - Purpose: Creates the compile script and compiles the model (with execute option)
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-j, --jobs [number of jobs to run simultneously]`
        - `-n, --parallel [number of concurrent modile compiles]`
        - `-e, --execute`

``create-dockerfile``
-------------

`fre make create-dockerfile [options]`
   - Purpose: Creates the dockerfile and creates the container (with execute option)
   - With the creation of the dockerfile, the Makefile, checkout script, and any other necessary script is copied into the container from a temporary location
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`

``run-fremake``
-------------

`fre make run-fremake [options]`
   - Purpose: Create the checkout script, Makefile, compile script, and dockerfile (platform dependent) for the compilation of the model
   - Options:
        - `-y, --yamlfile [experiment yaml] (required)`
        - `-p, --platform [platform] (required)`
        - `-t, --target [target] (required)`
        - `-npc, --no-parallel-checkout (for container build)`
        - `-j, --jobs [number of jobs to run simultneously]`
        - `-n, --parallel [number of concurrent modile compiles]`
