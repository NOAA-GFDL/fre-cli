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

# Test individual functions operating correctly: combine and validate
def test_correct_combine():
    ''' test that combined yaml includes necessary keys '''
    p = "None"
    t = "None"
    yamlfilepath = Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    # Combine model / experiment
    try:
        yml_dict = list_experiments_script.quick_combine(yamlfilepath,EXP_NAME,p,t)
    except:
        assert 1 == 2

    req_keys = ["name","platform","target","fre_properties","experiments"]
    for k in req_keys:
        assert k in yml_dict.keys()

@pytest.mark.skip(reason='cannot validate with current schema at the moment')
def test_yamlvalidate():
    ''' test yaml is being validated '''
    yamlfilepath = Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    # Combine model / experiment
    yml_dict = list_experiments_script.quick_combine(yamlfile_path, EXP_NAME, PLATFORM, TARGET)

    # Validate and capture output
    assert helpers.validate_yaml(yml_dict, VAL_SCHEMA)
