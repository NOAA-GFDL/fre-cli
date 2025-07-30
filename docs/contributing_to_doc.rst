.. last updated early Jul 9 2025.

``fre-cli``'s documentation is built with ``sphinx`` and written in restructured-text.
A decent cheat-sheet for restructured-text can be found 
`at this gist <https://gist.github.com/SMotaal/24006b13b354e6edad0c486749171a70#sections>`__.

with a PR to NOAA-GFDL/fre-cli (recommended)
--------------------------------------------

This approach is the easiest, most-automated we have to offer open-source contributors. It is completely appropriate
for casual editing of the docs and previewing the changes, all while not eating up your personal github account's free
CI/CD minutes, and making PR reviews incredibly easy for documentation changes.

* you DO NOT NEED a ``readthedocs.org`` account.
* Make a branch, either with ``NOAA-GFDL/fre-cli`` as the remote, or your own fork.
* Edit a file any non-zero amount, commit that change to your branch, and push. If the branch is idential to ``main``,
  you cannot open a PR!
* Once the PR is opened, a ``readthedocs`` workflow will be run, even if that PR is in draft mode. To confirm it is
  running, or did run, open your PR in a web browser, scroll to the bottom to find the latests workflow runs under
  "checks", and click the ``readthedocs`` workflow.
* after clicking, you should see a URL like ``https://noaa-gfdl--<PR_NUMBER>.org.readthedocs.build/projects/fre-cli/en/<PR_NUMBER>/``,
  where ``<PR_NUMBER>`` is the PR number, for examples, these doc updates were added in PR `530 <https://github.com/NOAA-GFDL/fre-cli/pull/530>`_ .
* If the doc build is successful, you should see the usual ``fre-cli`` documentation page. If unsuccessful, you should
  see a ``404`` error.
* To review documentation differences, play with the "Show diff" checkbox, which gives an explicit visual difference
  highlight right on the built webpage


with a fork and your own readthedocs account
--------------------------------------------

This approach is good for playing with configuration of the workflow and not making a lot of noise on the main repository
with one's development. If you want to experiment more freely and not send notifications to every maintainer of ``fre-cli``,
this is for you. It also won't use your own github account minutes.

* Make sure you HAVE a fork underneath your github profile, if not, fork the repository under the NOAA-GFDL namespace
* Navigate to readthedocs' `log-in page <https://app.readthedocs.org/accounts/signup/>`_ and sign in with your GitHub
  account. This effectively creates a ``readthedocs.org`` account for you, attached to your ``github`` account. 
* Click "Add project" and search for ``fre-cli``. If your fork doesn't automatically come up, you do not have a fork!
  Go back to the first step in this list.
* If your changes do not live on a branch named ``main`` (they should not, at least), configure the project to look
  for your branch's name.
* If perms and everything lines up right, on your next push to the aforementioned branch, the docs should build and
  offer a preview relatively quickly. You should not have to re-configure anything to get it to work.


local sphinx build
------------------

This is good for deep debugging of the documentation build.

prereq: local conda environment and ``fre-cli``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
First, get a local conda
`env <https://noaa-gfdl.github.io/fre-cli/setup.html#create-environment-from-github-repo-clone>`_ of
``fre-cli`` going. This is required because ``sphinx`` uses python's ``importlib`` functionality to
auto-generate a clickable module-index from doc-strings.


install ``sphinx`` and related packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from the root-directory of your local repository copy, issue the following commands.

.. code-block:: console

 pip install .[docs]
 sphinx-apidoc --output-dir docs fre/ --separate
 sphinx-build docs build

Then, to view the result, open up the resultant ``fre-cli/build/index.html`` with your favorite web browser.
You should be able to click around the locally built html and links should work as expected.

.. note:: There will be a complaint regarding the ``pytest`` and ``coverage`` badges being absent. These are ``svg``
          images that are generated on-the-fly with ``genbadge`` in the CI/CD context. One can simply copy the current
          badges on the ``fre-cli`` README into the ``docs`` folder with the specific paths shown in ``sphinx``\'s
          complaint.

.. note:: ``sphinx-build`` is quite permissive, though loud. It makes accurate and numerous complaints, but often
          is able to successfully finish anyways. After the first successful build, many warnings will not be displayed
          a second time unless the file throwing the warning was changed. To get all the (useful AND useless) build
          output like the first run, simply add ``-E`` or ``--fresh-env`` to the call to avoid using ``sphinx``\'s
          build-cache.
