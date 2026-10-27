## Release Versioning Procedure
Note: [fre-cli](https://github.com/NOAA-GFDL/fre-cli) and [fre-postprocess-workflow](https://github.com/NOAA-GFDL/fre-postprocess-workflow) are versioned together. When fre-cli deploys a new release, a corresponding release is deployed in fre-postprocess-workflow.

## Checklist
### fre-postprocess-workflow changes
* [ ] 1. Create corresponding tag in [fre-postprocess-workflow](https://github.com/NOAA-GFDL/fre-postprocess-workflow/tags) (See fre-cli changes (3) for how to tag)

    **Note**: The workflow no longer hard-codes the fre-cli version. `fre pp configure-yaml` sets `FRE_VERSION` in
    `rose-suite.conf` to `$(fre --version)`, and the workflow loads the matching `fre/<version>` module.
    For development versions (ending in `-dev`), `FRE_VERSION` is set to `test` instead, i.e. the `fre/test` module.

### fre-cli changes
* [ ] 2. Verify that git submodules in the fre-cli reflect the latest state (or certain commit/tag) of the upstream repositories. 

    - If not, consult the manager of the upstream repository and determine whether the update should be included in this FRE release.
    - If so, ask the sub-project maintainer to tag the upstream repository

    Open a PR to commit the submodule updates in `fre-cli`, solicit a review, and merge the PR.
       
    - **Submodules**:
        - `fre/gfdl_msd_schemas`
        - `fre/mkmf`

    **Note**: The release schedules of these submodules may vary from that of fre-cli

* [ ] 3. Create a tag in the fre-cli repository (testing tag or release tag)

    Locally this can be done with:

    ```
    git tag -a <release>
    git push origin <tag name>
    ```

    - For the *testing tags*, follow the structure: `[year].[major].[minor].[testing tag]`

        - `[year].[major].[minor].alpha[iteration]`: alpha tags include major code breaking changes
        - `[year].[major].[minor].beta[iteration]`: beta tags include releases candidates for testing

    - For the *full release tag*, follow the structure: `[year].[major].[minor]`

    After the tag is pushed, CI (`.github/workflows/update_tag.yaml`) will trigger the creation of a PR that changes any
    reference to the previous tag to the new tag, and sets the version in `fre/__init__.py` to `<new tag>-dev`.
    Untagged states of `main` between tags (e.g. `fre/test`) report `<last tag>-dev` with `fre --version`.
    Verify the tagged release is present [here](https://github.com/NOAA-GFDL/fre-cli/releases>)

    This PR will need to be closed and reopened to run CI testing. Review and merge it: **merging this PR publishes the
    release conda package** (`.github/workflows/publish_conda.yml`), versioned as the tag without `-dev`.

    **NOTE**: Previously, the PR creation did not always update version references correctly. Check the PR's diff, and
    if references to the previous tag remain in the documentation or fre-cli tests, update them manually.

* [ ] 4. For a full release (only), create a the github release associated with the correct tag and generate the release notes.

    - In the release notes, be sure to link any alpha and beta tags that were tested for the release

* [ ] 5. Navigate to [noaa-gfdl conda channel](https://anaconda.org/NOAA-GFDL/fre-cli) and verify that the last upload date corresponds to the date of this release and that the release number is correct.

    - Once installed, `fre --version` from the release package should report the tag, without a `-dev` suffix.
