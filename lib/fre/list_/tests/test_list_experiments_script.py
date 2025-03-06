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

def test_exp_list(capfd):
    ''' test list exps '''
    list_experiments_script.list_experiments_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    #Capture output
    out,err=capfd.readouterr()
    if "Post-processing experiments available" in out:
        assert True
    else:
        assert False

def test_int_combine(capfd):
    ''' test intermediate combine step is happening '''
    list_experiments_script.list_experiments_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    #Capture output
    out,err=capfd.readouterr()
    check_out = ["Combining yaml files", "model yaml"]
    for i in check_out:
        if i in out:
            assert True
        else:
           assert False

def test_nocombinedyaml():
    ''' test intermediate combined yaml was cleaned at end of listing '''
    assert Path(f"./combined-{EXP_NAME}.yaml").exists() == False

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
        if k in y.keys():
            assert True
        else:
            assert False   

def test_yamlremove():
   ''' test intermediate combined yaml removed '''
   # Remove combined yaml file
   list_experiments_script.remove(f"combined-{EXP_NAME}.yaml")

   assert Path(f"./combined-{EXP_NAME}.yaml").exists() == False
