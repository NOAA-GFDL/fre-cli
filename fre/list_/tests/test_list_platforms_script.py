"""
Test fre list platforms
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_platforms_script

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
PLATFORM = "None"
TARGET = "None"
YAMLFILE = "null_model.yaml"
BADYAMLFILE = "null_model_bad.yaml"
EXP_NAME = YAMLFILE.split(".")[0]

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


def test_nocombinedyaml():
    ''' test intermediate combined yaml was cleaned '''
    assert not Path(f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml").exists()

# Test individual functions operating correctly: combine and clean
def test_correct_combine():
    ''' test that combined yaml includes necesary keys '''
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Combine model / experiment
    list_platforms_script.quick_combine(yamlfile_path,PLATFORM,TARGET)
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml").exists()

    comb_yamlfile = f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml"
    with open(comb_yamlfile, 'r') as yf:
        y = yaml.load(yf,Loader=yaml.Loader)

    req_keys = ["name","platform","target","platforms"]
    for k in req_keys:
        assert k in y.keys()

def test_yamlvalidate(caplog):
    ''' test yaml is being validated '''
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Combine model / experiment
    list_platforms_script.quick_combine(yamlfile_path,PLATFORM,TARGET)
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml").exists()

    comb_yamlfile = f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml"
    with open(comb_yamlfile, 'r') as yf:
        y = yaml.load(yf,Loader=yaml.Loader)

    # Validate and capture output
    assert list_platforms_script.validate_yaml(y)
    #assert "Intermediate combined yaml VALID" in caplog.text


#def test_not_valid_yaml():

def test_yamlremove():
   ''' test intermediate combined yaml removed '''
   # Remove combined yaml file
   list_platforms_script.remove(f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml")

   assert not Path(f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml").exists()
