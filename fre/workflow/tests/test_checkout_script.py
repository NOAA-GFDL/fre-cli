''' fre workflow checkout tests '''
import re
from pathlib import Path
import pytest
from fre.workflow import checkout_script

TEST_CONFIGS = "fre/workflow/tests/AM5_example/"
EXPERIMENT = "c96L65_am5f7b12r1_amip_TESTING"

#@pytest.fixture(autouse=True, name="fake_home")
#def fake_home_fixture(tmp_path, monkeypatch):
#    """
#    Set the tmp_path as HOME for the cylc-src directory
#    to be created in.
#    """
#    ## Mock HOME for cylc-src and cylc-run
#    fake_home = Path(tmp_path)
#    monkeypatch.setenv("HOME", str(fake_home))
#
#    return fake_home
#
def test_cylc_src_creation_fail(tmp_path):
    """
    Test for the expected failure if the cylc-src
    directory cannot be created. 

    This test simulates a file with the name cylc-src
    already created, causing a permission error in HOME.
    """
    cylc_src_file = Path(f"{tmp_path}/cylc-src")
    with open(cylc_src_file, "w", encoding='utf-8') as f:
        f.write("testing 123")

    # run checkout to create cylc-src
    directory = Path(f"{tmp_path}/cylc-src")
    expected_error = f"(checkoutScript) directory {directory} wasn't able to be created. exit!"
    with pytest.raises(OSError, match = re.escape(expected_error)):
        checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                          experiment = EXPERIMENT,
                                          application = "pp",
                                          target_dir = tmp_path)

def test_checkout_target_dir_dne(tmp_path):
    """
    """
    bad_dir = "does/not/exist"

    # run checkout to create cylc-src
    expected_error = f"Target directory {bad_dir} does not exist or cannot be found."

    with pytest.raises(ValueError, match = re.escape(expected_error)):
        checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                          experiment = EXPERIMENT,
                                          application = "pp",
                                          target_dir = bad_dir)

def test_checkout_missing_repo(tmp_path):
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
                                          application = "pp",
                                          target_dir = tmp_path)

#def test_run_workflow_checkout(caplog):
#    """
#    Test for a successful run workflow checkout.
#    """
#    checkout_script.workflow_checkout(yamlfile,
#                                      experiment = "c96L65_am5f7b12r1_amip_TESTING",
#                                      application = "run")

def test_pp_workflow_checkout(tmp_path, caplog):
    """
    Test for a successful post-processing workflow checkout.
    """
    checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                      experiment = EXPERIMENT,
                                      application = "pp",
                                      target_dir = tmp_path)

    expected_repo = "https://github.com/NOAA-GFDL/fre-workflows.git"
    expected_tag = "main"
    assert all([Path(f"{tmp_path}/cylc-src/{EXPERIMENT}").exists(),
                Path(f"{tmp_path}/cylc-src/{EXPERIMENT}").is_dir(),
                Path(f"{tmp_path}/cylc-src/{EXPERIMENT}/flow.cylc").exists(),
                Path(f"{tmp_path}/cylc-src/{EXPERIMENT}/config.yaml").exists(),
                f"({expected_repo}):({expected_tag}) check out ==> SUCCESSFUL" in caplog.text])

def test_pp_workflow_checkout_exists_already(tmp_path, caplog):
    """
    Test for the expected output message if the checkout/branch already exists.
    """
    # 1st checkout
    checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                      experiment = EXPERIMENT,
                                      application = "pp",
                                      target_dir = tmp_path)

    # 2nd checkout
    checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                      experiment = EXPERIMENT,
                                      application = "pp",
                                      target_dir = tmp_path)

    repo = "https://github.com/NOAA-GFDL/fre-workflows.git"
    expected_tag = "main"
    expected_output = [
                       f"({repo}):({expected_tag}) check out ==> REQUESTED",
                       (f"Checkout exists ('{tmp_path}/cylc-src/c96L65_am5f7b12r1_amip_TESTING'), "
                        f"and matches '{expected_tag}'")
                      ]

    for string in expected_output:
        assert string in caplog.text

##def test_pp_workflow_checkout_force_checkout
