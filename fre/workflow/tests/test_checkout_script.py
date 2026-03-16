''' fre workflow checkout tests '''
import re
from pathlib import Path
import pytest
from fre.workflow import checkout_script

TEST_CONFIGS = "fre/workflow/tests/AM5_example/"
EXPERIMENT = "c96L65_am5f7b12r1_amip_TESTING"

def test_cylc_src_creation_fail(tmp_path):
    """
    Test for the expected failure if the cylc-src
    directory cannot be created. 

    This test simulates the instance where a file with the name
    'cylc-src' already exists, causing a permission error in HOME.
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

def test_checkout_invalid_resolved_yaml(tmp_path):
    """
    Test for the expected error if the repository is not
    defined in the settings.yaml and the yamls could not
    be combined
    """
    experiment = "c96L65_am5f7b12r1_amip_TESTING_WRONG"
    repo = None
    tag = "main"
    with pytest.raises(ValueError, match = f"Combined yaml is not valid. Please fix the errors and try again."):
        checkout_script.workflow_checkout(yamlfile = f"{TEST_CONFIGS}/am5.yaml",
                                          experiment = experiment,
                                          application = "pp",
                                          target_dir = tmp_path)

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
                Path(f"{tmp_path}/cylc-src/{EXPERIMENT}/config.yaml").exists()])

def test_pp_workflow_checkout_exists_already(tmp_path, caplog):
    """
    Test for the expected output message if the checkout already exists,
    using the same branch.
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
                       (f"Checkout exists ('{tmp_path}/cylc-src/c96L65_am5f7b12r1_amip_TESTING'), "
                        f"and matches '{expected_tag}'")
                      ]

    for string in expected_output:
        assert string in caplog.text

def test_pp_workflow_checkout_force_checkout(tmp_path, caplog):
    """
    Test successful re-cloning of the workflow repo
    when force-checkout=True.
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
                                      target_dir = tmp_path,
                                      force_checkout = True)

    src_dir = f"{tmp_path}/cylc-src"
    workflow_name = EXPERIMENT
    repo = "https://github.com/NOAA-GFDL/fre-workflows.git"
    tag = "main"
    expected_output = f" *** REMOVING {src_dir}/{workflow_name} *** "

    assert expected_output in caplog.text

#def test_run_workflow_checkout(caplog):
#    """
#    Test for a successful run workflow checkout.
#    """
#    checkout_script.workflow_checkout(yamlfile,
#                                      experiment = "c96L65_am5f7b12r1_amip_TESTING",
#                                      application = "run")
