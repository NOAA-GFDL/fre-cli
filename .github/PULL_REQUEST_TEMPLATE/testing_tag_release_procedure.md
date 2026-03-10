## Testing Release Versioning Procedure
Note: [fre-cli](https://github.com/NOAA-GFDL/fre-cli) and [fre-workflows](https://github.com/NOAA-GFDL/fre-workflows) are versioned together. When fre-cli deploys a new release, a corresponding release is deployed in fre-workflows.

## Checklist
### fre-cli changes
* [ ] 1. Verify that git submodules in the fre-cli reflect the latest state (or certain commit/tag) of the upstream repositories. 

    - If not, consult the manager of the upstream repository and determine whether the update should be included in this FRE release.
    - If so, ask the sub-project maintainer to tag the upstream repository, and then commit the submodule update in `fre-cli`.
       
    - **Submodules**:
        - `fre/gfdl_msd_schemas`
        - `fre/mkmf`
        - `fre/tests/test_files/cmip6-cmor-tables`
        - `fre/tests/test_files/cmip7-cmor-tables`

    **Note**: The release schedules of these submodules may vary from that of fre-cli

* [ ] 2. Create a tag in the fre-cli repository (testing tag or release tag)

    Locally this can be done with:

    ```
    git tag -a <release>
    git push --tags
    ```

    The tag format can be followed: `[year].[major].[minor]-[testing tag]`

    For the testing tags:

        - `[year].[major].[minor]-alpha[iteration]`: alpha tags relate to major code breaking changes
        - `[year].[major].[minor]-beta[iteration]`: beta tags relate to minor changes

    After the tag is pushed, CI will trigger the creation of a PR changing any reference to the previous tag with the new tag.  Review the PR and merge.
    Verify the tagged release is present [here](https://github.com/NOAA-GFDL/fre-cli/releases>)

* [ ] 3. Update the tag release number in your PR branch before merging to `main`

    - Edit tag mention in `fre/tests/test_fre_cli.py`
