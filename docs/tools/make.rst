==========================
Make Subcommands Reference
==========================

checkout
========

``fre make checkout-script [options]`` [cite: 2]

**Purpose:**
  Writes a script that will clone (checkout) the model code from respective git repositories[cite: 3].

**Options:**
  -y, --yamlfile [model yaml file]  (required): Model configuration yaml FILENAME[cite: 5].
  -p, --platform [platform]        (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument[cite: 6].
  -t, --target [target]            (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument[cite: 7].
  -gj, --gitjobs [number]          Number of git submodules to clone simultaneously (optional) (default 4)[cite: 8].
  -npc, --no-parallel-checkout     Turns off parallel git clones. By default, fre make will clone each git repository in parallel[cite: 9].
  -e, --execute                    Execute the checkout script immediately following its generation[cite: 10]. The default behavior is to generate the script, but not execute[cite: 11].
  --force-checkout                 Force a git checkout if the source directory already exists[cite: 12].

---

makefile
========

``fre make makefile [options]`` [cite: 14]

**Purpose:**
  Writes a Makefile that will compile the model code[cite: 15].

**Options:**
  -y, --yamlfile [model yaml file]  (required): Model configuration yaml FILENAME[cite: 17].
  -p, --platform [platform]        (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument[cite: 18].
  -t, --target [target]            (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument[cite: 19].

---

compile
=======

``fre make compile-script [options]`` [cite: 21]

**Purpose:**
  Writes a compile script that will configure the compile environment and execute make[cite: 22].

**Options:**
  -y, --yamlfile [model yaml file]  (required): Model configuration yaml FILENAME[cite: 24].
  -p, --platform [platform]        (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument[cite: 25].
  -t, --target [target]            (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument[cite: 26].
  -mj, --makejobs [number]         Number of make recipes to compile simultaneously (optional) (default 4)[cite: 27].
  -n, --nparallel [number]         Number of concurrent compile scripts to execute (optional) (default 1)[cite: 28]. This option is ignored when the argument --execute/-e is missing[cite: 29].
  -e, --execute                    Execute the compile script immediately following its generation[cite: 30]. The default behavior is to generate the script, but not execute[cite: 31].
  -v, --verbose                    Turns on debug level logging[cite: 32].

---

dockerfile
==========

``fre make dockerfile [options]`` [cite: 34]

**Purpose:**
  Writes a Dockerfile and createContainer.sh script that will generate a container image (.sif format) containing the source code, Makefile, model executable, and dependent libraries[cite: 35].

**Options:**
  -y, --yamlfile [model yaml file]  (required): Model configuration yaml FILENAME[cite: 37].
  -p, --platform [platform]        (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument[cite: 38].
  -t, --target [target]            (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument[cite: 39].
  -nft, --no-format-transfer       Skip the container format conversion to a Singularity Image File (.sif)[cite: 40].
  -e, --execute                    Execute the createContainer script immediately following its generation[cite: 41]. The default behavior is to generate the script, but not execute[cite: 42].

---

all
===

``fre make all [options]`` [cite: 44]

**Purpose:**
  Executes the above fre make subcommands in the appropriate order to generate a model executable or container image (platform dependent)[cite: 45].

**Options:**
  -y, --yamlfile [model yaml file]  (required): Model configuration yaml FILENAME[cite: 47].
  -p, --platform [platform]        (required) (repeatable): FRE platform string. Define multiple platforms by repeating this argument[cite: 48].
  -t, --target [target]            (required) (repeatable): mkmf target string. Define multiple targets by repeating this argument[cite: 49].
  -n, --nparallel [number]         Number of concurrent compile scripts to execute (optional) (default 1)[cite: 50]. This option is ignored when the argument --execute/-e is missing[cite: 51].
  -mj, --makejobs [number]         Number of make recipes to compile simultaneously (optional) (default 4)[cite: 52].
  -gj, --gitjobs [number]          Number of git submodules to clone simultaneously (optional) (default 4)[cite: 53].
  -npc, --no-parallel-checkout     Turns off parallel git clones. By default, fre make will clone each git repository in parallel[cite: 54].
  -nft, --no-format-transfer       Skip the container format conversion to a Singularity Image File (.sif)[cite: 55].
  -e, --execute                    Execute the checkout and compile/createContainer scripts immediately following their generation[cite: 56]. The default behavior is to generate the scripts, but not execute[cite: 57].
  --force-checkout                 Force a git checkout if the source directory already exists[cite: 58].
  -v, --verbose                    Turns on debug level logging[cite: 59].
