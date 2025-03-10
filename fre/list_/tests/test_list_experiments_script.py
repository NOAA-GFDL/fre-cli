"""
Test fre list exps
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_experiments_script

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
YAMLFILE = "null_model.yaml"
EXP_NAME = "None"

# yaml file checks
def test_modelyaml_exists():
    ''' Make sure model yaml exists '''
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}").exists()

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


def test_nocombinedyaml():
    ''' test intermediate combined yaml was cleaned at end of listing '''
    assert not Path(f"./combined-{EXP_NAME}.yaml").exists()

# Test individual functions operating correctly: combine and clean
def test_correct_combine():
    ''' test that combined yaml includes necessary keys '''
    p = "None"
    t = "None"
    yamlfilepath = Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    # Combine model / experiment
    list_experiments_script.quick_combine(yamlfilepath,EXP_NAME,p,t)
    assert Path(f"./combined-{EXP_NAME}.yaml").exists()

    with open(f"combined-{EXP_NAME}.yaml", 'r') as yf:
        y = yaml.load(yf,Loader=yaml.Loader)

    req_keys = ["name","platform","target","fre_properties","experiments"]
    for k in req_keys:
        assert k in y.keys()


def test_yamlremove():
   ''' test intermediate combined yaml removed '''
   # Remove combined yaml file
   list_experiments_script.remove(f"combined-{EXP_NAME}.yaml")

   assert not Path(f"./combined-{EXP_NAME}.yaml").exists()
