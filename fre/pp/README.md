




<!-- this section seems more general than should be in fre/pp
# **Frepp Canopy**
_Brief description of tool group's purpose._

* [Tool Group] Supports:
   - _List_
   - _of_
   - _supported_
   - _features_

* **_Any notes/warnings for user_**

The [tool group] fre-cli tools are described below ([Subcommands](#subcommands)) as well as a Guide on the order in which to use them (Guide).

## **Usage (Users)**
* Refer to fre-cli [README.md](https://github.com/NOAA-GFDL/fre-cli/blob/main/README.md) for foundational fre-cli usage guide and tips.
* [tool group] package repository located at: _insert permalink_

## Subcommands
- `fre [tool group] [subcommand] [options]`
   - Purpose: _Insert subcommand purpose_
   - Options:
        - `-[short command], --[long command] [name of argument] (required/not required)`
## Guide
### **[Certain type of build/run]:**
```bash
# Short description of subcommand 1
fre [tool group] [subcommand] -[short/long command 1] [argument(s) 1] -[short/long command 2] [argument(s) 2] etc.

# Short description of subcommand 2
fre [tool group] [subcommand] -[short/long command 1] [argument(s) 1] -[short/long command 2] [argument(s) 2] etc.

# Short description of subcommand 3
fre [tool group] [subcommand] -[short/long command 1] [argument(s) 1] -[short/long command 2] [argument(s) 2] etc.

etc.
```
-->

## **Quickstart instructions to postprocess FMS history output on PP/AN or gaea**

1. Checkout postprocessing workflow template
This will clone the postprocessing repository into `/home/$USER/cylc-src/EXPNAME__PLATFORM__TARGET`.
```
module load fre/canopy
fre pp checkout -e EXPNAME -p PLATFORM -t TARGET
```

2. Configure pp template with either XML or pp.yaml

```
fre pp configure-xml -e EXPNAME -p PLATFORM -t TARGET -x XML
```
or
```
fre pp configure-yaml -e EXPNAME -p PLATFORM -t TARGET -y YAML 

```

3. (OPTIONAL BUT RECOMMENDED) Create `history-manifest` for config validation

Create a `history-manifest` of a single tar file archive first for use in the validation. 
This list represents the available source files within the history tar archives, and enables the 
validation procedure to catch a wider variety of potential errors. This can be done like so-
```
tar -tf /archive/$USER/path/to/history/files/YYYYMMDD.nc.tar | grep -v tile[2-6] | sort > /home/$USER/cylc-src/EXPNAME__PLATFORM__TARGET/history-manifest
```

4. Validate the configuration
```
fre pp validate -e EXPNAME -p PLATFORM -t TARGET
```

Warnings related to directories are probably valid and should be fixed in `rose-suite.conf`, or created as necessary via `mkdir`.

If you are running postprocessing gaea, you'll need to change the `SITE` variable in `rose-suite.conf` from `ppan` to `gaea`.

5. Install the workflow

```
fre pp install -e EXPNAME -p PLATFORM -t TARGET
```

If you are attempting this on gaea, you'll need to make two one-time changes before installing.
- Currently, `cylc`, `rose`, and `isodatetime` must be in your PATH for new shells. One approach to do this is
to symlink the fms-user-installed fre-cli cylc/rose/isodatetime scripts into your local `~/bin` directory,
and then add that `~/bin` directory to your PATH in your `.bashrc` or `.cshrc`. (If you don't do this, Cylc tasks
will fail complaining those 3 tools are not available.)

```
cd ~/bin
ln -s /ncrc/home2/Flexible.Modeling.System/conda/envs/fre-cli/bin/{cylc,rose,isodatetime} .
echo 'setenv PATH ${PATH}:~/bin' >> ~/.cshrc
```
- Currently, the cylc available on gaea (through `module load cylc` or the `PATH` trick above) does not
include any global configuration, so you'll need to create a file `~/.cylc/flow/global.cylc` that contains the following.
If you don't do this, Cylc will use your home directory for the scratch space and rapidly fill your quota.)

```
[install]
    [[symlink dirs]]
        [[[localhost]]]
            run = /gpfs/f5/scratch/gfdl_f/$USER
```

6. Run the workflow

```
fre pp run -e EXPNAME -p PLATFORM -t TARGET
```

7. Report status of workflow progress

```
fre pp status -e EXPNAME -p PLATFORM -t TARGET
```

8. Launch GUI

```
TODO: fre pp gui?

The full GUI can be launched on jhan or jhanbigmem (an107 or an201).

cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
```

## **PP Wrapper Usage**

```
fre pp all -e EXPNAME -p PLATFORM -t TARGET
```

### **PP Wrapper Decision Tree**
![pp_wrapper_decsiontree](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/d3eaa237-1e29-4922-9d83-8d9d11925c54)

### **Tests**

To run `fre pp` tests, return to root directory of the fre-cli repo and call just those tests with

    python -m pytest fre/pp/tests/[test script.py]

Or run all tests with

    python -m pytests fre/pp/tests
