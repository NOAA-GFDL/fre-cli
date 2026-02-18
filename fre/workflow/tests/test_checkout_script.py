''' fre workflow checkout tests '''
import stat
import re
import os
from pathlib import Path
import pytest
from fre.workflow import checkout_script

TEST_CONFIGS = "fre/workflow/tests/AM5_example/"
EXPERIMENT = "c96L65_am5f7b12r1_amip_TESTING"

@pytest.fixture(autouse=True, name="fake_home")
def fake_home_fixture(tmp_path, monkeypatch):
    """
    Set the tmp_path as HOME for the cylc-src directory
    to be created in.
    """
    ## Mock HOME for cylc-src and cylc-run
    fake_home = Path(tmp_path)
    monkeypatch.setenv("HOME", str(fake_home))

    return fake_home

def test_cylc_src_creation_fail(fake_home):
    """
    Test for the expected failure if the cylc-src
    directory cannot be created. 

    This test simulates a permission error in HOME.
    """
    try:
        # Temporarily change fake_home permissions to read-only for usr/owner
        # If read-only, cylc-src dir creation should fail
        Path(fake_home).chmod(stat.S_IRUSR)

        # run checkout to create cylc-src
        directory = Path(f"{fake_home}/cylc-src")
        expected_error = f"(checkoutScript) directory {directory} wasn't able to be created. exit!"
        with pytest.raises(OSError, match = re.escape(expected_error)):
            checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                              experiment = EXPERIMENT,
                                              application = "pp")
    finally:
        Path(fake_home).chmod(stat.S_IRWXU)

def test_check_missing_repo():
    """
    Test for the expected ValueError if the repo is not
    defined in the settings.yaml.
    """
    experiment = "c96L65_am5f7b12r1_amip_TESTING_WRONG"
    repo = None
    tag = "main"
    with pytest.raises(ValueError, match = f"One of these are None: repo / tag = {repo} / {tag}"):
        checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                          experiment = experiment,
                                          application = "pp")

#def test_run_workflow_checkout(caplog):
#    """
#    Test for a successful run workflow checkout.
#    """
#    checkout_script.workflow_checkout(yamlfile,
#                                      experiment = "c96L65_am5f7b12r1_amip_TESTING",
#                                      application = "run")

def test_pp_workflow_checkout(fake_home, caplog):
    """
    Test for a successful post-processing workflow checkout.
    """
    checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                      experiment = EXPERIMENT,
                                      application = "pp")

    expected_repo = "https://github.com/NOAA-GFDL/fre-workflows.git"
    expected_tag = "main"
    assert all([Path(f"{fake_home}/cylc-src/{EXPERIMENT}").exists(),
                Path(f"{fake_home}/cylc-src/{EXPERIMENT}").is_dir(),
                Path(f"{fake_home}/cylc-src/{EXPERIMENT}/flow.cylc").exists(),
                Path(f"{fake_home}/cylc-src/{EXPERIMENT}/config.yaml").exists(),
                f"({expected_repo}):({expected_tag}) check out ==> SUCCESSFUL" in caplog.text])

def test_pp_workflow_checkout_exists_already(fake_home, caplog):
    """
    Test for the expected output message if the checkout/branch already exists.
    """
    # 1st checkout
    checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                      experiment = EXPERIMENT,
                                      application = "pp")

    # 2nd checkout
    checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                      experiment = EXPERIMENT,
                                      application = "pp")

    repo = "https://github.com/NOAA-GFDL/fre-workflows.git"
    expected_tag = "main"
    expected_output = [
                       f"({repo}):({expected_tag}) check out ==> REQUESTED",
                       (f"Checkout exists ('{fake_home}/cylc-src/c96L65_am5f7b12r1_amip_TESTING'), "
                        f"and matches '{expected_tag}'")
                      ]

    for string in expected_output:
        assert string in caplog.text

#def test_pp_workflow_checkout_branch_override(caplog):
#    """
#    Test for correct checkout if a '-b', '--branch' is specified.
#    """
#    checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
#                                      experiment = EXPERIMENT,
#                                      application = "pp",
#                                      branch = "2025.04")
#
#    repo = "https://github.com/NOAA-GFDL/fre-workflows.git"
#    expected_tag = "2025.04"
#    expected_output = [f"({repo}):({expected_tag}) check out ==> REQUESTED",
#                       f"({repo}):({expected_tag}) check out ==> SUCCESSFUL"]
#
#    for string in expected_output:
#        assert string in caplog.text
#
#def test_pp_workflow_checkout_branch_conflict(fake_home, caplog):
#    """
#    Test for the expected ValueError if the checkout was done already,
#    but user is checking out same repo again, with a different branch/tag.
#    """
#    # 1st checkout: using default 'main' branch as set in the settings.yaml (version)
#    checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
#                                      experiment = EXPERIMENT,
#                                      application = "pp",
#                                      branch = None)
#
#    expected_output = (f"ERROR: Checkout exists ('{fake_home}/cylc-src/{EXPERIMENT}') "
#                        "and does not match '2025.04'")
#    expected_error = "Neither tag nor branch matches the git clone branch arg"
#    with pytest.raises(ValueError, match = expected_error):
#        # 2nd checkout: trying to check out 2025.04 tag while 'main' already checked out
#        checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
#                                          experiment = EXPERIMENT,
#                                          application = "pp",
#                                          branch = "2025.04")
#    assert expected_output in caplog.text
