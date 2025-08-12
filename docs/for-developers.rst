==============
For developers
==============

Developers should consult this section for detailed and specific information relevant to development/maintenance efforts,
AFTER familiarizing themselves with the rest of the user-targeted documentation. Some material in this section is
earmarked as specific to maintaining the code repository (see :ref:`repository-maintenance`).


Contributing to ``fre-cli``
===========================


Get a Copy of the Code
----------------------
Get your own copy of the code with ``git clone --recursive git@github.com:NOAA-GFDL/fre-cli.git`` for the NOAA-GFDL fork,
or replace with your fork's link (recommended).


Local/Editable Installation
---------------------------
Developers can test local changes by running a ``pip install [-e] .`` inside of the root directory after activating a
virtual environment with ``python>=3.11.*`` and all requirements. This installs the ``fre-cli`` package locally with
any local changes.

Development work on ``fre-cli`` should occur within a conda environment housing ``fre-cli``'s requirements, and
a local copy of the repository to install with ``pip`` using the ``-e/--editable`` flag on. This specific approach is
described in :ref:`setup`.


Testing Your Local Changes and Installation
-------------------------------------------
There are a myriad of different ways of testing your efforts locally during your development cycle. A few examples and
``fre-cli`` specific recommendations are described here, but contributors are welcome to be creative so-long as they
provide documentation of what they have contributed.

All contributed code should come with a corresponding unit-test. This section is not about writing unit-tests, but does
contain some advice towards it. This section is mostly for streamlining a new developer's approach to working with the
code.


Running CLI-calls
~~~~~~~~~~~~~~~~~
Most development cycles will involve focused efforts isolated to a specific ``fre TOOL COMMAND *ARGV``, where ``*ARGV``
stands in for a shell-style argument vector (e.g. ``-e FOO -p BAR -t BAZ``, a common pattern in ``fre-cli``). Likely, the
code one is working on here is housed somewhere *approximately* like ``fre/TOOL/COMMAND.py`` (*generally*, this is not a
law), with the ``click`` CLI entry-point under ``fre/TOOL/freTOOL.py``.

Here, the developer usually uses the ``fre TOOL COMMAND *ARGV`` call as a test, focused on seeing the changes they are
introducing, and develop the code until they see the result they are looking for. The specific ``fre TOOL COMMAND *ARGV``
should/can often become a unit-test in one of the corresponding files in ``fre/tests``. The sought-after changes the
developer wished to introduce should become ``assert`` conditions encoded within the unit-test. Both success and failure
conditions should ideally be tested. 


Running the above, with no ``click``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Every ``fre TOOL COMMAND *ARGV`` approximately maps to a single function call shown in ``fre/TOOL/freTOOL.py`` at this time.
Then, to accomplish the same thing as the previous section, but removing ``click`` and the CLI-aspect from it, and assuming
the code being executed is in ``fre/TOOL/COMMAND.py``, in a function called named like ``FUNCTION``,
``python -i -c 'from fre.TOOL.COMMAND import FUNCTION; FUNCTION(**args);``.


Writing a ``pytest`` unit-test for ``fre-cli``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If the functionality one desires to test is that of CLI call, the tests should use the ``CliRunner`` approach shown in
``fre/tests``. ``click`` based CLI calls should NOT be tested with ``subprocess.run`` ever within ``pytest``. See
`click's documentation <https://click.palletsprojects.com/en/stable/testing/#testing-click-applications>`_ for more
information.

If the functionality one desires to test is removed from that of a CLI call, the test should likely be housed in the directory
structure corresponding to the ``TOOL`` under-which the functionality lives. In that case, the usual pythonic-testing
approaches, guidelines, documentation etc. applies.


Adding a New Requirement to ``fre-cli``
---------------------------------------
Currently, all required packages are ``conda`` packages listed in ``environment.yml``, and also, equivalently in ``meta.yaml``.
``conda`` packages that have a corresponding ``pip`` package should list the ``pip`` package as a python requirement in
``setup.py``.

Pure ``pip`` packages cannot be listed currently as a requirement for ``fre-cli``. This is because only ``environment.yml`` can
list ``pip`` packages as requirements. But, only ``meta.yaml`` can be used as a the ``conda build`` target. New dependencies
for ``fre-cli`` MUST have a ``conda`` package available through a non-proprietary ``conda`` channel, but preferable the
open-source ``conda-forge`` channel, which requires stronger quality control.

In general, the requirement being added is created by a third-party. As such, before adding a new requirement, the developer is
responsible for verifying that the desired package is safe, well-documented, and actively-maintained as necessary. The developer should
also consider the cost-benefit-problem of taking the extra time to introduce new functionality via standard-library approaches first,
and be prepared to defend the proposition of adding the new third-party package as a ``fre-cli`` requirement.


How ``fre-cli`` is updated
--------------------------
``fre-cli`` is published and hosted as a Conda package on the NOAA-GFDL `conda channel <https://anaconda.org/NOAA-GFDL>`_. On
pushes to the ``main`` branch, the package located at https://anaconda.org/NOAA-GFDL/fre-cli will automatically be updated using
the workflow defined in ``.github/workflows/publish_conda.yml``, which is equivalent to ``.github/workflows/build_conda.yml``
with an extra ``conda publish`` step.


Get desired ``logging`` verbosity
---------------------------------

The ``logging`` module's configuration initially occurs in ``fre/__init__.py``, and gets inherited everywhere else ``logging``
creates a ``logger`` object under the ``fre.`` namespace. If your development is being tested with a ``fre TOOL COMMAND *ARGV``
style CLI call, it's recommended you add verbosity flags, i.e. like ``fre -vv TOOL COMMAND *ARGV``.

If your development does not fit nicely into that category, the next easiest thing to do is to adjust the base ``logger`` object
in ``fre/__init__.py`` to have the verbosity level you'd like. It's important you adjust it back to the default verbosity level of
``fre-cli`` before requesting a merge of your branch/fork to the repository's trunk.


``logging`` practice to avoid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The pitfall to avoid during development is calling ``logging.basicConfig`` to re-configure the ``logging`` behavior OUTSIDE of
``fre/__init__.py``. What this does is it creates another ``logging.handler`` to manage the output, but does not resolve
the ambiguity to previously defined ``loggers`` of which ``handler`` should be getting used. If this secondary ``logging.basicConfig``
call is left in the PR or fork at merge-time, it can cause oddly silent logging behavior. This can be VERY tricky to debug!

avoid ``os.chdir`` if you can
-----------------------------

Directory changing in ``python`` is not transient by-default, i.e., if when running ``fre`` the interpreter changes directories,
then the result of a ``os.cwd()`` later in the program may be changed to an unexpected value, leading to difficult bugs.

This being said, sometimes an ``os.chdir`` is hard to not want to use. If one has to use directory changing instead of managing
directory targets explicitly as ``pathlib.Path`` instances, then one can use the following logic to safely ``chdir`` where needed
and ``chdir`` back:

.. code-block:: python

 go_back_here = os.cwd()
 try:
   os.chdir(target_dir)
   # DO STUFF AFTER CHDIR HERE
 except:
   raise Exception('some error explaining what went wrong')
 finally:
   os.chdir(go_back_here)


``MANIFEST.in``
---------------

In the case where non-python files like templates, examples, and outputs are to be included in the ``fre-cli`` package,
``MANIFEST.in`` can provide the solution. Ensure that the file exists within the correct folder, and add a line to the
``MANIFEST.in`` file saying something like ``include fre/fre<tool>/fileName.fileExtension``

* For more efficiency, if there are multiple files of the same type needed, the ``MANIFEST.in`` addition can be something
  like ``recursive-include fre/fre<tool> *.fileExtension`` which would recursively include every file matching that
  ``fileExtension`` within the specified directory and its respective subdirectories.

.. _repository-maintenance:

repository maintenance
======================

.. include:: for-maintainers.rst
