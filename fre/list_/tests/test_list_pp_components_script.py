"""
Test fre list pp-comps
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_pp_components_script
from fre.yamltools import combine_yamls_script as cy
from fre.yamltools import helpers

# SET-UP
TEST_DIR = Path("fre/pp/tests")
AM5_EXAMPLE = Path("AM5_example")
MODEL_YAMLFILE = "am5.yaml"
SETTINGS_YAMLFILE = "yaml_include/settings.yaml"
PP_YAMLFILES = ["yaml_include/pp.c96_amip.yaml", "yaml_include/pp-test.c96_amip.yaml", "yaml_include/settings.yaml"]
EXP_NAME = "c96L65_am5f7b12r1_amip"
VAL_SCHEMA = Path("fre/gfdl_msd_schemas/FRE/fre_pp.json")
PLATFORM = "FOO"
TARGET = "BAR"

# yaml file checks
def test_modelyaml_exists():
    ''' Test model yaml exists '''
    assert Path(f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}").exists()

def test_settingsyaml_exist():
    ''' Test settings yaml exists '''
    assert Path(f"{TEST_DIR}/{AM5_EXAMPLE}/{SETTINGS_YAMLFILE}").exists()

def test_ppyamls_exist():
    ''' Test post-processing yamls exist '''
    for pp_yaml in PP_YAMLFILES:
        assert Path(f"{TEST_DIR}/{AM5_EXAMPLE}/{pp_yaml}").exists()

# Test whole tool
def test_exp_list(caplog):
    ''' Test fre list pp-components subtool '''
    list_pp_components_script.list_ppcomps_subtool(f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}", EXP_NAME)

    # check the logging output
    check_out = [ 'Components to be post-processed:',
                  '   - atmos',
                  '   - atmos_scalar']

    for i in check_out:
        assert i in caplog.text
        
    # make sure the level is INFO
    for record in caplog.records:
        assert record.levelname == "INFO"

# Test validation
def test_yamlvalidate(caplog):
    ''' Test yaml is being validated '''
    # Combine model / experiment
    list_pp_components_script.list_ppcomps_subtool(f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}", EXP_NAME)

    validate = ["Validating YAML information...",
                "     YAML dictionary VALID."]

    for i in validate:
        assert i in caplog.text

    for record in caplog.records:
        record.levelname == "INFO"
