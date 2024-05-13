# **FRE-CLI**

FMS Runtime Environment (FRE) CLI developed using Python's Click package

## **Background**

As part of fre/canopy, MSD wanted to develop a modern, user-friendly CLI that will allow users to call upon FRE commands using a **_fre_** **tool** _subtool_ syntax. Developed with Click, a Python package easily installable through PyPI and Conda, the main goal of this is to allow users access to most, if not all of MSD-managed tools and workflows from one packaged, centralized CLI.

![Screenshot from 2024-04-18 13-42-04](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/43c028a6-4e6a-42fe-8bec-008b6758ea9b)

![clidiagram](https://github.com/NOAA-GFDL/fre-cli/assets/98476720/04cd8ce1-dec8-457f-b8b7-544275e04f46)

## **Usage (Users)**

* Accessing the fre-cli:
    - (Method 1) User - Loading module:
        - workstation: `module load fre/canopy`
        - gaea: `module load fre/canopy`
    - (Method 2) User - Conda environment setup
        - If on workstation:
            - `module load miniforge`
            - `conda activate /nbhome/fms/conda/envs/fre-cli`
        - If on gaea:
            - `module load miniforge`
            - `conda activate /ncrc/home2/Flexible.Modeling.System/conda/envs/fre-cli`
    - (Method 3) Developer - If you have Conda loaded and want to create your OWN environment (i.e. for development, testing, etc.)
            - Create a new Conda environment: `conda create -n [environmentName]`
            - Append necessary channels
                - `conda config --append channels noaa-gfdl` 
                - `conda config --append channels conda-forge`
            - Run `conda install` on needed dependencies (`conda install click` will give you access to pip as well)
                - `conda install noaa-gfdl::fre-cli` should install the [CLI package](https://anaconda.org/NOAA-GFDL/fre-cli) created from the [`meta.yaml`](https://github.com/NOAA-GFDL/fre-cli/blob/refactoring/meta.yaml)
            - All other dependencies used by the tools are installed along with this install (configured inside the meta.yaml), with the exception of local modules
            - setup.py file allows [`fre.py`](https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/fre.py) to be ran with `fre` as the entry point on the command line instead of `python fre.py`
* Enter commands and follow `--help` messages for guidance (brief rundown of commands also provided below)
    - If the user just runs `fre`, it will list all the command groups following `fre`, such as `run`, `make`, `pp`, etc. and once the user specifies a command group, the list of available subcommands for that group will be shown 
    - Commands that require arguments to run will alert user about missing arguments, and will also list the rest of the optional parameters if `--help` is executed
        - Argument flags are not positional, can be specified in any order as long as they are specified
* Can run directly from any directory, no need to clone repository
* *May need to deactivate environment and reactivate it in order for changes to apply*

### **Commands/Tools Included**

To be developed:
- [ ]  **fre check**
- [x]  **fre app**
- [x]  **fre catalog**
- [ ]  **fre list**
- [x]  **fre make**
- [x]  **fre cmor**
- [ ]  **fre run**
- [ ]  **fre test**
- [ ]  **fre yamltools**

## **Usage (Developers)**

* Developers are free to use the user guide above to familiarize with the CLI and save time from having to install any dependencies, but development within a Conda environment is heavily recommended regardless
* Gain access to the repository with `git clone git@github.com:NOAA-GFDL/fre-cli.git` or your fork's link (recommended) and an SSH RSA key
    - Once inside the repository, developers can test local changes by running a `pip install .` inside of the root directory to install the fre-cli package locally with the newest local changes on top of the installed Conda fre-cli dependencies
    - Test as a normal user would use the CLI
* Create a GitHub issue to reflect your contribution's background and reference it with Git commits

### **Adding New Commands/Tools - Checklist**

If there is *no* subdirectory created for the new tool command group you are trying to develop, there are a few steps to follow:

  1. Create a subdirectory for the tool group inside the /fre folder; i.e. `/fre/tool`
  2. Add an `__init__.py` inside of the new subdirectory
      - this will contain as many lines as needed for each tool subcommand feature (function/class), following the syntax: `from .subCommandScript import subCommandFunction` or `from .subCommandScript import subCommandClass`
      - at the end of the `__init__.py` file, add an `__all__` [variable](https://realpython.com/python-all-attribute/), following [this syntax](https://github.com/NOAA-GFDL/fre-cli/blob/refactoring/fre/pp/__init__.py): `__all__ = ["subCommandFunction1", "subCommandFunction2", "subCommandClass1", "subCommandClass2"]`
      - the purpose of these lines are to enable `fre.py` to invoke them using its own [`__init__.py`](https://github.com/NOAA-GFDL/fre-cli/blob/refactoring/fre/__init__.py
  3. Create separate files to house the code implementation for each different subcommand; *do not* include any Click decorators for your function, except for `@click.command`
      - Define the function with its usual arguments, and the Click decorators to prompt them will go into `fre[tool].py`
  4. Remember to import any needed packages/dependencies in your subcommand script file
  5. _As of second refactoring_: Create a file named `fre[tool].py` (i.e `fremake.py`)
  6. In `fre[tool].py`, import all script commands from the tool's `__init__.py` file (i.e. `from .tool import subCommandFunction1, subCommandClass1, etc.`), and create a `@click.group` called `[tool]Cli` that is simply passed to the `if __name__ == "__main__":` block at the bottom of the file
  7. Using `@[tool]Cli.command()`, add the `@click.option` and any other [Click attributes/decorators](https://click.palletsprojects.com/en/8.1.x/api/#click.command) needed
      - The commands within `fre[tool].py` must contain an additional decorator after the arguments, options, and other command components: `@click.pass_context`
      - Add `context` and the other decorator attributes into the function declaration (i.e. `def subCommand(context, yaml, platform, target)`) 
      - Add a `""" - [description] """` to help describe the command and pass `context.foward(subCommandFunction)` inside of the command to let it invoke the functions from outside files
  8. If the tool group is not already added into the `__init__.py` in the /fre folder, add it using `from .tool import *`
  9. With the lazy groups implemented in `lazy_group.py`, all that needs to be done is to add to the `lazy_subcommands` defined inside of the main `@click.group`, `fre`, inside of `fre.py`
      - Add the line: `"[tool]": ".[tool].fre[tool].[tool]Cli"`
      - (Recommended): If the update is significant, consider incrementing the version number within [`setup.py`](https://github.com/NOAA-GFDL/fre-cli/blob/088ad363392b3bf187119d8970c22779d59aaed0/setup.py#L5) to reflect and signify the changes 
  10. Test by running `pip install .` from the root level of the directory, and running `fre`, followed by any subcommands necessary
 
### **Adding Tools From Other Repositories**

* Currently, the solution to this task is to approach it using Conda packages. The tool that is being added must reside within a repository that contains a meta.yaml that includes Conda dependencies like the one in this repository and ideally a setup.py (may be subject to change due to deprecation) that may include any potentially needed pip dependencies
    - Once published as a Conda package, ideally on the [NOAA-GFDL channel](https://anaconda.org/NOAA-GFDL), an addition can be made to the "run" section under the "requirements" category in the meta.yaml of the fre-cli following the syntax `channel::package`
    - On pushes to the main branch, the [package](https://anaconda.org/NOAA-GFDL/fre-cli) will automatically be updated using the workflow file
 
### **MANIFEST.in**

* In the case where non-python files like templates, examples, and outputs are to be included in the fre-cli package, MANIFEST.in can provide the solution. Ensure that the file exists within the correct folder, and add a line to the MANIFEST.in following [this syntax](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html)
    - For more efficiency, if there are multiple files of the same type needed, the MANIFEST.in addition can be something like `recursive-include fre/fre(subTool) *.fileExtension` which would recursively include every file matching that fileExtension within the specified directory and its respective subdirectories. Currently, fre-cli recursively includes every python and non-python file inside of /fre, although this may change in the future
    - `setup.py` handles these files using [setuptools and namespace package finding](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html)

### **Example /fre Directory Structure**
```
.
├── __init__.py
├── fre.py
├── /tool
│   ├── __init__.py
│   └── subCommandScript.py
```

## **Additional Helpful Links**
* [Official Click Documentation](https://click.palletsprojects.com/en/8.1.x/api/)
* [`setup.py` key words](https://setuptools.pypa.io/en/latest/references/keywords.html)
