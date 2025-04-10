"""
Test fre list pp-comps
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_pp_components_script
from fre.yamltools import helpers

# SET-UP
TEST_DIR = Path("fre/pp/tests")
AM5_EXAMPLE = Path("AM5_example")
MODEL_YAMLFILE = "am5.yaml"
PP_YAMLFILES = ["yaml_include/pp.c96_amip.yaml", "yaml_include/pp-test.c96_amip.yaml", "yaml_include/settings.yaml"]
EXP_NAME = "c96L65_am5f7b12r1_amip"
VAL_SCHEMA = Path("fre/gfdl_msd_schemas/FRE/fre_pp.json")
PLATFORM = "FOO"
TARGET = "BAR"

# yaml file checks
def test_modelyaml_exists():
    ''' Make sure model yaml exists '''
    assert Path(f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}").exists()

def test_ppyamls_exist():
    ''' Make sure pp yamls exist '''
    for pp_yaml in PP_YAMLFILES:
        assert Path(f"{TEST_DIR}/{AM5_EXAMPLE}/{pp_yaml}").exists()

# Test whole tool
def test_exp_list(caplog):
    ''' test list exps '''
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

# Test individual functions operating correctly: combine and validation
def test_correct_combine():
    ''' test that combined yaml includes necesary keys '''
    yamlfile_path = f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}"

    # Combine model / experiment
    try:
        yml_dict = list_pp_components_script.quick_combine(yamlfile_path, EXP_NAME, PLATFORM, TARGET)
    except:
        assert 1 == 2

    req_keys = ["name", "directories", "postprocess"]
    for k in req_keys:
        assert k in yml_dict.keys()

def test_yamlvalidate():
    ''' test yaml is being validated '''
    yamlfile_path = f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}"

    # Combine model / experiment
    yml_dict = list_pp_components_script.quick_combine(yamlfile_path, EXP_NAME, PLATFORM, TARGET)

    # Validate and capture output
    assert helpers.validate_yaml(yml_dict, VAL_SCHEMA)
