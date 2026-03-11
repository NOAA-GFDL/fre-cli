## Release Versioning Procedure
Note: [fre-cli](https://github.com/NOAA-GFDL/fre-cli) and [fre-workflows](https://github.com/NOAA-GFDL/fre-workflows) are versioned together. When fre-cli deploys a new release, a corresponding release is deployed in fre-workflows.

## Checklist
### fre-cli changes
* [ ] 1. Verify that git submodules in the fre-cli reflect the latest state (or certain commit/tag) of the upstream repositories. 

    - If not, consult the manager of the upstream repository and determine whether the update should be included in this FRE release.
    - If so, ask the sub-project maintainer to tag the upstream repository

    Open a PR to commit the submodule updates in `fre-cli`, solicit a review, and merge the PR.
       
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

    - For the *testing tags*, follow the structure: `[year].[major].[minor]-[testing tag]`

        - `[year].[major].[minor]-alpha[iteration]`: alpha tags include major code breaking changes
        - `[year].[major].[minor]-beta[iteration]`: beta tags include releases candidates for testing

    - For the *full release tag*, follow the structure: `[year].[major].[minor]`

    After the tag is pushed, CI will trigger the creation of a PR changing any reference to the previous tag with the new tag.
    Verify the tagged release is present [here](https://github.com/NOAA-GFDL/fre-cli/releases>)

* [ ] 3. For a full release (only), create a the github release associated with the correct tag and generate the release notes.

    - In the release notes, be sure to link any alpha and beta tags that were tested for the release

### fre-workflows changes
* [ ] 4. Update the package release number in the `fre-workflows` repository:

    - Edit `FRE_VERSION` in `flow.cylc`

* [ ] 5. Create corresponding tag in [fre-workflows](https://github.com/NOAA-GFDL/fre-workflows/tags)

* [ ] 6. Navigate to [noaa-gfdl conda channel](https://anaconda.org/NOAA-GFDL/fre-cli) and verify that the last upload date corresponds to the date of this release and that the release number is correct.
