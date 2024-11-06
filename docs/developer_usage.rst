===============
Developer Usage
===============

Developers are free to use the user guide above to familiarize with the CLI and save time from
having to install any dependencies, but development within a Conda environment is heavily
recommended regardless.

Gain access to the repository with ``git clone --recursive git@github.com:NOAA-GFDL/fre-cli.git`` or your fork's
link (recommended) and an SSH RSA key. Once inside the repository, developers can test local changes
by running a ``pip install .`` inside of the root directory to install the ``fre-cli`` package locally
with the newest local changes. Test as a normal user would use the CLI.


Adding New Tools
================


From Other Repositories
-----------------------

Currently, the solution to this task is to approach it using Conda packages. The tool that is being
added must reside within a repository that contains a ``meta.yaml`` that includes Conda dependencies
like the one in this repository and ideally a ``setup.py`` (may be subject to change due to deprecation)
that may include any potentially needed pip dependencies

* Once published as a Conda package, ideally on the `NOAA-GFDL conda channel <https://anaconda.org/NOAA-GFDL>`_,
  an addition can be made to the ``run`` section under ``requirements`` in ``meta.yaml`` of the ``fre-cli``
  following the syntax ``channel::package``

* On pushes to the main branch, the package located at https://anaconda.org/NOAA-GFDL/fre-cli will automatically
  be updated using by the workflow defined in ``.github/workflows/publish_conda.yml``
  

Checklist
---------

For the new tool you are trying to develop, there are a few criteria to satisfy

1. Create a subdirectory for the tool group inside the ``fre/`` directory; i.e. ``fre/<tool>``

2. Add an ``__init__.py`` inside of ``fre/<tool>`` 

* typically this file should be empty, but it depends on the ``<tool>``'s needs
* even if empty, the file facillitates module importability and must be present

3. Add a file named ``fre/<tool>/fre<tool>.py``. This will serve as the main entry point for ``fre``
   into the ``<tool>``'s functionality

4. Add a ``click`` group named after ``<tool>`` within ``fre/<tool>/fre<tool>.py``

* This ``click`` group will contain all the subcommands under the ``<tool>``'s functionality

5. Create separate files as needed for different subcommands; do not code out the full
   implemetation of ``<tool>`` inside of a ``click`` command within ``fre/<tool>/fre<tool>.py``.

* better yet, consider what structure your subtool may need in the future for maintainability's sake

6. Be sure to import the contents of the needed subcommand scripts inside of ``fre<tool>.py``

* i.e. from ``fre.fre<tool>.subCommandScript import *``

7. At this point, you can copy and paste the parts of your main ``click`` subcommand from its script
   into ``fre<tool>.py`` when implementing the function reflective of the subcommand function

* Everything will remain the same; i.e. arguments, options, etc.

* However, this new function within ``fre<tool>.py`` must a new line after the arguments, options,
  and other command components; ``@click.pass_context``

* Along with this, a new argument ``context`` must now be added to the parameters of the command
  (preferably at the beginning, but it won't break it if it's not)

8. From here, all that needs to be added after defining the command with a name is
   ``context.forward(mainFunctionOfSubcommand)``, and done!

9. After this step, it is important to add ``from fre.fre<tool> import`` to ``__init__.py``
   within the /fre folder

10. The last step is to replicate the subcommand in the same way as done in ``fre<tool>.py``
	inside of ``fre.py``, but make sure to add ``from fre import fre<tool>`` and
	``from fre.fre<tool>.fre<tool> import *``

Please refer to this issue when encountering naming issues:
`NOAA-GFDL#31 <https://github.com/NOAA-GFDL/fre-cli/issues/31>`_


Example ``fre/`` Directory Structure
------------------------------------

``fre/``
├── ``__init__.py``
├── ``fre.py``
├── ``fre<tool>``
│   ├── ``__init__.py``
│   ├── ``toolCommandScript.py``
│   └── ``fre<tool>.py``


``MANIFEST.in``
---------------

In the case where non-python files like templates, examples, and outputs are to be included in the ``fre-cli`` package,
``MANIFEST.in`` can provide the solution. Ensure that the file exists within the correct folder, and add a line to the
``MANIFEST.in`` file saying something like ``include fre/fre<tool>/fileName.fileExtension``

* For more efficiency, if there are multiple files of the same type needed, the ``MANIFEST.in`` addition can be something
  like ``recursive-include fre/fre<tool> *.fileExtension`` which would recursively include every file matching that
  ``fileExtension`` within the specified directory and its respective subdirectories.


Adding Documentation
--------------------

see section "Documentation-Documentation"




