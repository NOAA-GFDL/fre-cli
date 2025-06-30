==============
For maintainers
==============

Maintainers should consult this section for detailed and specific information relevant to maintaining github repositories, releasing, and deployments.


New Release Versioning Procedure
--------------------------------

1. Update the package release number (i.e. reported by `fre --version`) in your PR branch before merging to `main`
   a. edit `version` in setup.py
   b. edit two version mentions in fre/tests/test_fre_cli.py

2. Create tag in fre-cli (this repository) and associated github release
   a. locally this can be done with `git tag -a <release>` and `git push --tags`
   b. observe the tagged release here: https://github.com/NOAA-GFDL/fre-cli/releases

3. Create corresponding tag in [fre-workflows](https://github.com/NOAA-GFDL/fre-workflows/tags)

4. Observe new conda package deployed to [noaa-gfdl channel](https://anaconda.org/NOAA-GFDL/fre-cli)
