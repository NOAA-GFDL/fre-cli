"""
Test fre list exps
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_experiments_script
from fre.yamltools import helpers

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
YAMLFILE = "null_model.yaml"
EXP_NAME = "None"

# yaml file checks
def test_modelyaml_exists():
    ''' Make sure model yaml exists '''
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}").exists()

# Test whole tool
def test_exp_list(caplog):
    ''' test list exps '''
    list_experiments_script.list_experiments_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    # check the logging output
    check_out = [ 'Post-processing experiments available:',
                  '   - null_model_full',
                  '   - null_model_0',
                  '   - null_model_1',
                  '   - null_model_2'     ]
    for i in check_out:
        assert i in caplog.text
        
    # make sure the level is INFO
    for record in caplog.records:
        assert record.levelname == "INFO"

# Test validation
@pytest.mark.skip(reason='cannot validate with current schema at the moment. Current schemas include final "combined" schema to validate compile and pp information. Both of these "clean" the final yaml information for only what is needed. This final combined yaml info does not include the "experiments" section, which is the section being read and parsed for information')
def test_yamlvalidate():
    ''' test yaml is being validated '''
    yamlfilepath = Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    # Combine model / experiment
    yml_dict = list_experiments_script.list_experiments_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    # Validate and capture output
    assert helpers.validate_yaml(yml_dict, VAL_SCHEMA)
