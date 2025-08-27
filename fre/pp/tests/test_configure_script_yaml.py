"""
Test configure_script_yaml
"""
import os
import shutil
import yaml
from pathlib import Path
from fre.pp import configure_script_yaml as csy
from fre.yamltools import combine_yamls_script as cy
import pytest 
from jsonschema import validate, SchemaError, ValidationError

# Set what would be click options
EXPERIMENT = "c96L65_am5f7b12r1_amip"
PLATFORM = "gfdl.ncrc5-intel22-classic"
TARGET = "prod-openmp"

# Set example yaml paths, input directory
TEST_DIR = Path("fre/pp/tests")
TEST_YAML = Path("AM5_example/am5.yaml")

def test_combinedyaml_exists():
    """
    Make sure combined yaml file exists
    """
    assert Path(f"{TEST_DIR}/{TEST_YAML}").exists()

def test_configure_script():
    """
    Tests success of configure yaml script
    Creates rose-suite, regrid rose-app, remap rose-app
    TO-DO: will break this up for better tests
    """
    # Set home for ~/cylc-src location in script
    old_home = os.environ["HOME"]
    os.environ["HOME"] = str(Path(f"{TEST_DIR}/configure_yaml_out"))

    # Set output directory
    OUT_DIR = Path(f"{os.getenv('HOME')}/cylc-src/{EXPERIMENT}__{PLATFORM}__{TARGET}")
    Path(OUT_DIR).mkdir(parents = True, exist_ok = True)

    # Define combined yaml
    model_yaml = f"{TEST_DIR}/{TEST_YAML}"

    # Invoke configure_yaml_script.py
    csy.yaml_info(model_yaml, EXPERIMENT, PLATFORM, TARGET)

    os.environ["HOME"] = old_home

    # Check for configuration creation and final combined yaml
    assert all([ Path(f"{OUT_DIR}/{EXPERIMENT}.yaml").exists(),
                 Path(f"{OUT_DIR}/rose-suite.conf").exists(),
                 Path(f"{OUT_DIR}/app/regrid-xy/rose-app.conf").exists(),
                 Path(f"{OUT_DIR}/app/remap-pp-components/rose-app.conf").exists() ])

def test_validate():
    """
    Test the success of validation.
    """
    yml_dict = cy.consolidate_yamls(yamlfile = f"{TEST_DIR}/{TEST_YAML}",
                                 experiment = EXPERIMENT,
                                 platform = PLATFORM,
                                 target = TARGET,
                                 use = "pp",
                                 output = None)
    try:
        csy.validate_yaml(yml_dict)
    except:
        assert False

def test_validate_fail():
    """
    Test that validation fails when given the wrong yaml dictionary.
    """
    yml_dict = cy.consolidate_yamls(yamlfile = f"{TEST_DIR}/{TEST_YAML}",
                                 experiment = EXPERIMENT,
                                 platform = PLATFORM,
                                 target = TARGET,
                                 use = "pp",
                                 output = f"{Path(__file__).parent}/csy_out.yaml")

    # Missing history_dir, ptmp_dir, and postprocess
    wrong_yml_dict = {
                       "name": "exp_name",
                       "platform": "ptest",
                       "target": "ttest",
                       "directories": {"pp_dir": "/some/path"} 
                     }
    with pytest.raises(ValueError, match="Combined yaml is not valid. Please fix the errors and try again.") as execinfo:
        val_fail = csy.validate_yaml(wrong_yml_dict)

    assert execinfo.type is ValueError

def test_cleanup():
    shutil.rmtree(f"{TEST_DIR}/configure_yaml_out")
    assert not Path(f"{TEST_DIR}/configure_yaml_out").exists()
