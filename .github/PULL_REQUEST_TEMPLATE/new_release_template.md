## Release Versioning Procedure
Note: [fre-cli](https://github.com/NOAA-GFDL/fre-cli) and [fre-workflows](https://github.com/NOAA-GFDL/fre-workflows) are versioned together. When fre-cli deploys a new release, a corresponding release is deployed in fre-workflows.

## Checklist
* [ ] 1. Verify that git submodules in the fre-cli reflect the latest state (or certain commit/tag) of the upstream repositories. 

    - If not, consult the manager of the upstream repository and determine whether the update should be included in this FRE release.
    - If so, ask the sub-project maintainer to tag the upstream repository, and then commit the submodule update in `fre-cli`.
       
    - Submodules:
        - `fre/gfdl_msd_schemas`
        - `fre/mkmf`
        - `fre/tests/test_files/cmip6-cmor-tables`
        - `fre/tests/test_files/cmip7-cmor-tables`

    **Note**: The release schedules of these submodules may vary from that of fre-cli

* [ ] 2. Update the package release number (i.e. reported by `fre --version`) in your PR branch before merging to `main`

    - Edit two version mentions in `fre/tests/test_fre_cli.py`
  
* [ ] 3. Create a tag in the fre-cli repository and associated github release

    - locally this can be done with `git tag -a <release>` and `git push --tags`
    -  after the tag is pushed, CI will trigger the creation of a PR changing any reference to the previous tag with the new tag.  Review the PR and merge.
    - verify the tagged release is present [here](https://github.com/NOAA-GFDL/fre-cli/releases>)

* [ ] 4. Update the package release number in the `fre-workflows` repository:

    - Edit `FRE_VERSION` in `flow.cylc`

* [ ] 5. Create corresponding tag in [fre-workflows](https://github.com/NOAA-GFDL/fre-workflows/tags)

* [ ] 6. Navigate to [noaa-gfdl conda channel](https://anaconda.org/NOAA-GFDL/fre-cli) and verify that the last upload date corresponds to the date of this release and that the release number is correct.
