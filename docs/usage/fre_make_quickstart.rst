Quickstart
-----------------
The quickstart instructions builds the null model using yaml files located in the fre-cli repository [here](https://github.com/NOAA-GFDL/fre-cli/tree/main/fre/make/tests/null_example)

Users can clone the fre-cli repository and invoke the commands below from the root of the repository. 

1. All-in-one fre make subtool:

`all` kicks off the compilation automatically

.. code-block::

    # Bare-metal: create and run checkout script, create makefile, create and RUN compile script to generate a model executable
    fre make all -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod --execute

    # Container: create checkout script, makefile, create dockerfile, and create and RUN the container build script to generate a model container
    fre make all -y fre/make/tests/null_example/null_model.yaml -p hpcme.2023 -t prod --execute

2. Bare-metal Build (Single target)

For the bare-metal build, the parallel checkout feature is the default behavior.

.. code-block::

  # Create and run checkout script
  fre make checkout-script -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod --execute

  # Create the Makefile
  fre make makefile -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod

  # Create and run the compile script
  fre make compile-script -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod --execute

3. Bare-metal Build (Multiple targets):

.. code-block::

    # Create and run checkout script
    fre make checkout-script -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

    # Create the Makefile
    fre make makefile -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod -t debug

    # Create and run a compile script for each target specified
    fre make compile-script -y fre/make/tests/null_example/null_model.yaml -p ncrc5.intel23 -t prod -t debug --execute

4. Container Build:

In order for the container to build successfully, the parallel checkout feature is disabled.

.. code-block::

    # Create checkout script
    fre make checkout-script -y fre/make/tests/null_example/null_model.yaml -p hpcme.2023 -t prod

    # Create the Makefile
    fre make makefile -y fre/make/tests/null_example/null_model.yaml -p hpcme.2023 -t prod

    # Create the Dockerfile and container build script
    fre make dockerfile -y fre/make/tests/null_example/null_model.yaml -p hpcme.2023 -t prod --execute
