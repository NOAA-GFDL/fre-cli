.. last updated early Nov 2024.
   could use some refinement

=============================
Contributing to Documentation
=============================
``fre-cli``'s documentation is built with ``sphinx`` and written in restructured-text.
A decent cheat-sheet for restructured-text can be found 
`here <https://gist.github.com/SMotaal/24006b13b354e6edad0c486749171a70#sections>`_


local sphinx build
==================


prereq: local conda environment and ``fre-cli``
-----------------------------------------------
First, get a local conda
`env <https://noaa-gfdl.github.io/fre-cli/setup.html#create-environment-from-github-repo-clone>`_ of
``fre-cli`` going. This is required because ``sphinx`` uses python's ``importlib`` functionality to
auto-generate a clickable module-index from doc-strings.


install ``sphinx`` and related packages
---------------------------------------
from the root-directory of your local repository copy, issue the following commands.

.. code-block:: console

 pip install sphinx renku-sphinx-theme sphinx-rtd-theme
 pip install --upgrade sphinx-rtd-theme
 sphinx-apidoc --output-dir docs fre/ --separate
 sphinx-build docs build

then, with your preferred web browser, open up the resultant ``fre-cli/build/index.html`` to click around
locally-built ``html`` files.


with a fork
===========


fork and poke at the settings
-----------------------------

* Fork ``fre-cli`` on github	 
* On github, navigate to your ``fre-cli`` fork, and click “settings”
* In “settings”, click “pages”
* In “pages”, under “build and deployment”, make sure “source” is set to “Deploy from a branch”
* Under that, find “Branch”, make sure the branch selected is ``gh-pages``
* The branch ``gh-pages`` is "automagic”- i.e. do not change anything about it nor create a new one,
  nor interact with anything in that branch directly


enable workflows for your fork
------------------------------
note: this step may depend on user-specific settings!
* Back on top where you found “settings”, find and click “actions” to the left
* Enable running the workflow actions assoc with the ``fre-cli`` repo under ``.github/workflows``


run your fork's first workflow
------------------------------
* The documentation builds as the last steps to ``create_test_conda_env.yml`` when theres a push to ``main``
* To get your first workflow run on your fork, comment out the ``github.ref == ‘refs/heads/main’`` bit
  so that it runs when you push to any branch, and make a small, trivial, commit somewhere to your
  remote fork
* You should be able to find the deployed webpage from a successful workflow at
  https://your_username.github.io/fre-cli (if you did not change the fork’s name from ``fre-cli``, that is)
* If you’re only editing docs, you can make the turn-around time on your workflow ~3 min faster by
  commenting-out the ``pylint`` and ``pytest`` steps in ``create_test_conda_env.yml``, and disable running the
  ``build_conda.yml`` workflow
