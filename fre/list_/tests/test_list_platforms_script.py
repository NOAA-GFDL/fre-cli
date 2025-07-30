"""
Test fre list platforms
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_platforms_script
from fre.yamltools import combine_yamls_script as cy

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
PLATFORM = None
TARGET = None
YAMLFILE = "null_model.yaml"
EXP_NAME = YAMLFILE.split(".")[0]
VAL_SCHEMA = Path("fre/gfdl_msd_schemas/FRE/fre_make.json")

# Bad yaml example
BADYAMLFILE_PATH = f"{TEST_DIR}/{NM_EXAMPLE}/wrong_model/wrong_null_model.yaml"


# yaml file checks
def test_modelyaml_exists():
    ''' Test model yaml exists '''
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}").exists()

def test_compileyaml_exists():
    ''' Test compile yaml exists '''
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/compile.yaml").exists()

def test_platformyaml_exists():
    ''' Test platforms yaml exists '''
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/platforms.yaml").exists()

# Test whole tool 
def test_platforms_list_correct(caplog):
    ''' Test fre list platforms subtool '''
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

# Test validation
def test_yamlvalidate(caplog):
    ''' Test yaml is being validated and is actually valid'''
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Combine model / experiment
    list_platforms_script.list_platforms_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    validate = ["Validating YAML information...",
                "     YAML dictionary VALID."]

    for i in validate:
        assert i in caplog.text

    for record in caplog.records:
        record.levelname == "INFO"

def test_not_valid_yaml():
    ''' Test the correct output matches the ValueError raised when yaml is invalid '''
    # Combine model / experiment
    with pytest.raises(ValueError, match="YAML dictionary NOT VALID."):
        list_platforms_script.list_platforms_subtool(f"{BADYAMLFILE_PATH}")
