==============
For maintainers
==============

Maintainers should consult this section for detailed and specific information relevant to maintaining github repositories, releasing, and deployments.


New Release Versioning Procedure
--------------------------------

1. Verify that git submodules `gfdl_msd_schemas` and `mkmf` reflect the latest state of the upstream repositories. If not, consult the manager of the upstream repository and determine whether the update should be included in this FRE release. If so, ask the sub-project maintainer to tag the upstream repository, and then commit the submodule update in fre-cli.

2. Update the package release number (i.e. reported by `fre --version`) in your PR branch before merging to `main`

   a. edit `version` in setup.py
   b. edit two version mentions in fre/tests/test_fre_cli.py

3. Create tag in fre-cli (this repository) and associated github release

   a. locally this can be done with `git tag -a <release>` and `git push --tags`
   b. observe the tagged release here: https://github.com/NOAA-GFDL/fre-cli/releases

4. Update the package release number in the fre-workflows repository:

   a. edit `FRE_VERSION` in flow.cylc (line 4)

5. Create corresponding tag in [fre-workflows](https://github.com/NOAA-GFDL/fre-workflows/tags)

5. Observe new conda package deployed to [noaa-gfdl channel](https://anaconda.org/NOAA-GFDL/fre-cli)
