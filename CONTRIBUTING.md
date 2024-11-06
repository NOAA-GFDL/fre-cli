## **For Developers**

* Developers are free to use this repository's `README.md` to familiarize with the CLI and save time from having to install any dependencies, but development within a Conda environment is heavily recommended regardless
* Gain access to the repository with `git clone --recursive git@github.com:NOAA-GFDL/fre-cli.git` or your fork's link (recommended) and an SSH RSA key
    - Once inside the repository, developers can test local changes by running a `pip install .` inside of the root directory to install the fre-cli package locally with the newest local changes on top of the installed Conda fre-cli dependencies
    - Test as a normal user would use the CLI
* Create a GitHub issue to reflect your contribution's background and reference it with Git commits

### **Opening Pull Requests and Issues**
Please use one of the templates present in this repository to open a PR or an issue, and fill out the template to the best of your ability.

### **Adding New Commands/Tools - Checklist**

If there is *no* subdirectory created for the new tool command group you are trying to develop, there are a few steps to follow:

  1. Create a subdirectory for the tool group inside the /fre folder; i.e. `/fre/tool`
  2. Add an `__init__.py` inside of the new subdirectory
      - this will contain as many lines as needed for each tool subcommand feature (function/class), following the syntax: `from .subCommandScript import subCommandFunction` or `from .subCommandScript import subCommandClass`
      - at the end of the `__init__.py` file, add an `__all__` [variable](https://realpython.com/python-all-attribute/), following [this syntax](https://github.com/NOAA-GFDL/fre-cli/blob/refactoring/fre/pp/__init__.py): `__all__ = ["subCommandFunction1", "subCommandFunction2", "subCommandClass1", "subCommandClass2"]`
      - the purpose of these lines are to enable `fre.py` to invoke them using its own [`__init__.py`](https://github.com/NOAA-GFDL/fre-cli/blob/refactoring/fre/__init__.py
  3. Create separate files to house the code implementation for each different subcommand; *do not* include any Click decorators for your function, except for `@click.command`
      - Define the function normally with its usual arguments; the Click decorators to prompt them will instead go into `fre[tool].py`
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
├── README-tool-template.md
├── lazy_group.py
├── /[tool]
│   ├── __init__.py
│   ├── fre[tool].py
│   ├── README.md
│   ├── [subCommandScript].py
│   └── /[optional-submodule]
```

## **Helpful Links**
* [Official Click Documentation](https://click.palletsprojects.com/en/8.1.x/api/)
* [`setup.py` Key Words](https://setuptools.pypa.io/en/latest/references/keywords.html)
* [`meta.yaml` Documentation](https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html)
