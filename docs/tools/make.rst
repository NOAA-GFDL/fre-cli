``checkout``
------------

``fre make checkout-script [options]``

**Purpose:**
  Writes a script that will clone (checkout) the model code from respective git repositories.

**Options:**
  - ``-y, --yamlfile [model yaml file]`` (required): Model configuration yaml FILENAME.
  - ``-p, --platform [platform]`` (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument.
  - ``-t, --target [target]`` (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument.
  - ``-gj, --gitjobs [number]`` Number of git submodules to clone simultaneously (optional) (default 4).
  - ``-npc, --no-parallel-checkout`` Turns off parallel git clones. By default, fre make will clone each git repository in parallel.
  - ``-e, --execute`` Execute the checkout script immediately following its generation. The default behavior is to generate the script, but not execute.
  - ``--force-checkout`` Force a git checkout if the source directory already exists.

---

``makefile``
------------

``fre make makefile [options]``

**Purpose:**
  Writes a Makefile that will compile the model code[

**Options:**
  - ``-y, --yamlfile [model yaml file]`` (required): Model configuration yaml FILENAME.
  - ``-p, --platform [platform]`` (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument.
  - ``-t, --target [target]`` (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument.

---

``compile``
-----------

``fre make compile-script [options]``

**Purpose:**
  Writes a compile script that will configure the compile environment and execute make.

**Options:**
  - ``-y, --yamlfile [model yaml file]`` (required): Model configuration yaml FILENAME.
  - ``-p, --platform [platform]`` (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument.
  - ``-t, --target [target]`` (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument.
  - ``-mj, --makejobs [number]`` Number of make recipes to compile simultaneously (optional) (default 4).
  - ``-n, --nparallel [number]`` Number of concurrent compile scripts to execute (optional) (default 1). This option is ignored when the argument --execute/-e is missing.
  - ``-e, --execute`` Execute the compile script immediately following its generation. The default behavior is to generate the script, but not execute.
  - ``-v, --verbose`` Turns on debug level logging.

---

``dockerfile``
--------------

``fre make dockerfile [options]``

**Purpose:**
  Writes a Dockerfile and createContainer.sh script that will generate a container image (.sif format) containing the source code, Makefile, model executable, and dependent libraries.

**Options:**
  - ``-y, --yamlfile [model yaml file]`` (required): Model configuration yaml FILENAME.
  - ``-p, --platform [platform]`` (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument.
  - ``-t, --target [target]`` (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument.
  - ``-nft, --no-format-transfer`` Skip the container format conversion to a Singularity Image File (.sif).
  - ``-e, --execute`` Execute the createContainer script immediately following its generation. The default behavior is to generate the script, but not execute.

---

``all``
-------

``fre make all [options]``

**Purpose:**
  Executes the above fre make subcommands in the appropriate order to generate a model executable or container image (platform dependent).

**Options:**
  - ``-y, --yamlfile [model yaml file]`` (required): Model configuration yaml FILENAME.
  - ``-p, --platform [platform]`` (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument.
  - ``-t, --target [target]`` (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument.
  - ``-n, --nparallel [number]`` Number of concurrent compile scripts to execute (optional) (default 1). This option is ignored when the argument --execute/-e is missing.
  - ``-mj, --makejobs [number]`` Number of make recipes to compile simultaneously (optional) (default 4).
  - ``-gj, --gitjobs [number]`` Number of git submodules to clone simultaneously (optional) (default 4).
  - ``-npc, --no-parallel-checkout`` Turns off parallel git clones. By default, fre make will clone each git repository in parallel.
  - ``-nft, --no-format-transfer`` Skip the container format conversion to a Singularity Image File (.sif).
  - ``-e, --execute`` Execute the checkout and compile/createContainer scripts immediately following their generation. The default behavior is to generate the scripts, but not execute.
  - ``--force-checkout`` Force a git checkout if the source directory already exists.
  - ``-v, --verbose`` Turns on debug level logging.
