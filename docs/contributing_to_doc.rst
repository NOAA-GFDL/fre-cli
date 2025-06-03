.. last updated early Nov 2024.
   could use some refinement

=============================
Contributing to Documentation
=============================
``fre-cli``'s documentation is built with ``sphinx`` and written in restructured-text.
A decent cheat-sheet for restructured-text can be found 
`here <https://gist.github.com/SMotaal/24006b13b354e6edad0c486749171a70#sections>`_


with a fork and readthedocs (recommended)
=========================================

This approach is good for casual editing of the docs and previewing the changes, all while not eating up your personal
github account's free CI/CD minutes. 

* Make sure you HAVE a fork underneath your github profile, if not, fork the repository under the NOAA-GFDL namespace
* Navigate to readthedocs' `log-in page <https://app.readthedocs.org/accounts/signup/>`_ and sign in with your GitHub
  account
* Click "Add project" and search for ``fre-cli``. If your fork doesn't automatically come up, you do not have a fork!
  Go back to the first step in this list.
* If your changes do not live on a branch named ``main`` (they should not, at least), configure the project to look
  for your branch's name.
* If perms and everything lines up right, on your next push to the aforementioned branch, the docs should build and
  offer a preview relatively quickly. You should not have to re-configure anything to get it to work.


local sphinx build
==================

This is good for deep debugging of the documentation build.

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

Then, to view the result, open up the resultant ``fre-cli/build/index.html`` with your favorite web browser.
You should be able to click around the locally built html and links should work as expected.

Note, there will be a complaint regarding the ``pytest`` and ``coverage`` badges being absent. These are ``svg``
images that are generated on-the-fly with ``genbadge`` in the CI/CD context. One can simply copy the current
badges on the ``fre-cli`` README into the ``docs`` folder with the specific paths shown in ``sphinx``\'s complaint.

Another note- ``sphinx-build`` is quite permissive, though loud. It makes accurate and numerous complaints, but often
is able to successfully finish anyways. After the first successful build, many warnings will not be displayed a second
time unless the file throwing the warning was changed. To get all the (useful AND useless) build output like the first
run, simply add ``-E`` or ``--fresh-env`` to the call to avoid using ``sphinx``\'s build-cache. 


with a fork and gh-pages
========================


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
