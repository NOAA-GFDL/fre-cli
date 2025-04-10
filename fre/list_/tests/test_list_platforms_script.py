"""
Test fre list platforms
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_platforms_script
from fre.yamltools import helpers

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
PLATFORM = "None"
TARGET = "None"
YAMLFILE = "null_model.yaml"
BADYAMLFILE = "null_model_bad.yaml"
EXP_NAME = YAMLFILE.split(".")[0]
VAL_SCHEMA = Path("fre/gfdl_msd_schemas/FRE/fre_make.json")

# yaml file checks
def test_modelyaml_exists():
    '''test if model yaml exists'''
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}").exists()

def test_compileyaml_exists():
    '''test if compile yaml exists'''
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/compile.yaml").exists()

def test_platformyaml_exists():
    '''test if platforms yaml exists'''
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/platforms.yaml").exists()

# Test whole tool 
def test_platforms_list(caplog):
    ''' test list platforms '''
    list_platforms_script.list_platforms_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    # check the logging output
    check_out = ["Platforms available:",
                 "    - ncrc5.intel23",
                 "    - hpcme.2023",
                 "    - ci.gnu",
                 "    - con.twostep"    ]
    for i in check_out:
        assert i in caplog.text

    # make sure level is INFO
    for record in caplog.records:
        record.levelname == "INFO"

# Test individual functions operating correctly: combine and validation
def test_correct_combine():
    ''' test that combined yaml includes necesary keys '''
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Combine model / experiment
    try:
        yml_dict = list_platforms_script.quick_combine(yamlfile_path,EXP_NAME, PLATFORM, TARGET)
    except:
        assert 1 == 2

    req_keys = ["name","platform","target","platforms"]
    for k in req_keys:
        assert k in yml_dict.keys()

def test_yamlvalidate():
    ''' test yaml is being validated '''
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Combine model / experiment
    yml_dict = list_platforms_script.quick_combine(yamlfile_path,EXP_NAME, PLATFORM, TARGET)

    # Validate and capture output
    assert helpers.validate_yaml(yml_dict, VAL_SCHEMA)

#def test_not_valid_yaml():
