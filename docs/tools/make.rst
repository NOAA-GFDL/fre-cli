``checkout``
------------

``fre make checkout-script [options]``
   - Purpose: Creates the checkout script and can check out source code (with execute option)
   - Options:
        - ``-y, --yamlfile [experiment yaml] (required)``
        - ``-p, --platform [platform] (required)``
        - ``-t, --target [target] (required)``
        - ``-gj, --gitjobs [number of submodules to clone in parallel]``
        - ``-npc, --no-parallel-checkout (for container build)``
        - ``-e, --execute``
        - ``force-checkout``

``makefile`` 
-------------

``fre make makefile [options]``
   - Purpose: Creates the makefile
   - Options:
        - ``-y, --yamlfile [experiment yaml] (required)``
        - ``-p, --platform [platform] (required)``
        - ``-t, --target [target] (required)``

``compile``
-----------

``fre make compile-script [options]``
   - Purpose: Creates the compile script and compiles the model (with execute option)
   - Options:
        - ``-y, --yamlfile [experiment yaml] (required)``
        - ``-p, --platform [platform] (required)``
        - ``-t, --target [target] (required)``
        - ``-mj, --makejobs [number of recipes from the Makefile to run in parallel]``
        - ``-n, --parallel [number of concurrent module compiles]``
        - ``-e, --execute``

``dockerfile``
--------------

``fre make dockerfile [options]``
   - Purpose: Creates the dockerfile and creates the container (with execute option)
   - With the creation of the dockerfile, the Makefile, checkout script, and any other necessary script is copied into the container from a temporary location
   - Options:
        - ``-y, --yamlfile [experiment yaml] (required)``
        - ``-p, --platform [platform] (required)``
        - ``-t, --target [target] (required)``
        - ``-nft, --no-format-transfer``
        - ``-e, --execute``

``all``
-------

``fre make all [options]``
   - Purpose: Create the checkout script, Makefile, compile script, and dockerfile (platform dependent) for the compilation of the model
   - Options:
        - ``-y, --yamlfile [experiment yaml] (required)``
        - ``-p, --platform [platform] (required)``
        - ``-t, --target [target] (required)``
        - ``-n, --parallel [number of concurrent module compiles]``
        - ``-mj --makejobs [number of recipes from the Makefile to run in parallel]``
        - ``-gj, --gitjobs [number of submodules to clone in parallel]`` 
        - ``-npc, --no-paralel-checkout``
        - ``-nft, --no-format-transfer``
        - ``-e, --execute``
