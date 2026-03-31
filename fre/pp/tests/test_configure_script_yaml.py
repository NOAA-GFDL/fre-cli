"""
Test configure_script_yaml
"""
import os
import shutil
from pathlib import Path

import pytest
import yaml
from jsonschema import (
    SchemaError,
    ValidationError,
    validate
)

import metomi.rose.config

from fre.pp import configure_script_yaml as csy
from fre.yamltools import combine_yamls_script as cy


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
                 Path(f"{OUT_DIR}/rose-suite.conf").exists()])

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
    with pytest.raises(
        ValueError,
        match="Combined yaml is not valid. Please fix the errors and try again."
    ) as execinfo:
        val_fail = csy.validate_yaml(wrong_yml_dict)

    assert execinfo.type is ValueError

def test_set_rose_suite_missing_postprocess():
    """
    Test that set_rose_suite raises ValueError when 'postprocess' section is missing.
    """
    rose_suite = metomi.rose.config.ConfigNode()
    yaml_dict = {
        "name": "exp_name",
        "platform": "ptest",
        "target": "ttest",
        "directories": {"pp_dir": "/some/path"}
    }
    with pytest.raises(ValueError):
        csy.set_rose_suite(yaml_dict, rose_suite)

def test_set_rose_suite_no_refinediag():
    """
    Test that set_rose_suite sets DO_REFINEDIAG to 'False' when no refinediag scripts are requested
    """
    rose_suite = metomi.rose.config.ConfigNode()
    yaml_dict = {
        "postprocess": {
            "settings": {"some_setting": "value"},
            "refinediag": {
                "example": {
                    "script": "/path/to/some/script",
                    "do_refinediag": False
                }
            }
        },
        "directories": {"pp_dir": "/some/path"},
    }
    csy.set_rose_suite(yaml_dict, rose_suite)
    assert rose_suite.get(['template variables', 'DO_REFINEDIAG']).value == 'False'

def test_set_rose_suite_no_preanalysis():
    """
    Test that set_rose_suite sets DO_PREANALYSIS to 'False' when no preanalysis scripts are requested
    """
    rose_suite = metomi.rose.config.ConfigNode()
    yaml_dict = {
        "postprocess": {
            "settings": {"some_setting": "value"},
            "preanalysis": {
                "example": {
                    "script": "/path/to/some/script",
                    "do_preanalysis": False
                }
            }
        },
        "directories": {"pp_dir": "/some/path"},
    }
    csy.set_rose_suite(yaml_dict, rose_suite)
    assert rose_suite.get(['template variables', 'DO_PREANALYSIS']).value == 'False'

def test_cleanup():
    shutil.rmtree(f"{TEST_DIR}/configure_yaml_out")
    assert not Path(f"{TEST_DIR}/configure_yaml_out").exists()

## to-do:
# - mock wrong schema path
# - any other raises missed
#def test_mock_validation_wrong_schema_path():
#    """
#    """
