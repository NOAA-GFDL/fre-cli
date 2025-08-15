
Maintainers should consult this section for detailed and specific information relevant to maintaining github repositories, releasing, and deployments.


Release Versioning Procedure
----------------------------
.. note:: `fre-cli <https://github.com/NOAA-GFDL/fre-cli>`__ and
          `fre-workflows <https://github.com/NOAA-GFDL/fre-workflows>`__ are versioned together.  When fre-cli deploys a new
          release, a corresponding release is deployed in fre-workflows

.. note:: `fre-cli <https://github.com/NOAA-GFDL/fre-cli>`__ has 3 submodules: 

          - `mkmf <https://github.com/NOAA-GFDL/mkmf>`__
          - `gfdl_msd_schemas <https://github.com/NOAA-GFDL/gfdl_msd_schemas>`__
          - `cmip6-cmor-tables <https://github.com/pcmdi/cmip6-cmor-tables>`__

          The release schedules of these submodules may vary from that of fre-cli

1. Verify that git submodules ``gfdl_msd_schemas`` and ``mkmf`` reflect the latest state of the upstream repositories.
   If not, consult the manager of the upstream repository and determine whether the update should be included in this
   FRE release. If so, ask the sub-project maintainer to tag the upstream repository, and then commit the submodule
   update in ``fre-cli``.

2. Update the package release number (i.e. reported by ``fre --version``) in your PR branch before merging to ``main``

   a. edit ``version`` in ``setup.py``
   b. edit two version mentions in ``fre/tests/test_fre_cli.py``
   c. Update release in ``docs/conf.py``

3. Create tag in fre-cli (this repository) and associated github release

   a. locally this can be done with ``git tag -a <release>`` and ``git push --tags``
   b. after the tag is pushed, CI will trigger the creation of a PR changing any reference to the previous tag with the
      new tag.  Review the PR and merge.
   c. verify the tagged release is present `here <https://github.com/NOAA-GFDL/fre-cli/releases>`_

4. Update the package release number in the ``fre-workflows`` repository:

   a. edit ``FRE_VERSION`` in ``flow.cylc`` (line 4)

5. Create corresponding tag in `fre-workflows <https://github.com/NOAA-GFDL/fre-workflows/tags>`_

6. Navigate to `noaa-gfdl conda channel <https://anaconda.org/NOAA-GFDL/fre-cli>`_  and verify that the last upload
   date corresponds to the date of this release and that the release number is correct. 
