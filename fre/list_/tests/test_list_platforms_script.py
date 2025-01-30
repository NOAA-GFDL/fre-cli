"""
Test fre list exps
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_platforms_script

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
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

def test_platforms_list(capfd):
    ''' test list exps '''
    list_platforms_script.list_platforms_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    #Capture output
    out,err=capfd.readouterr()
    if "Platforms available" in out:
        assert True
    else:
       assert False

def test_int_combine(capfd):
    ''' test intermediate combine is happening '''
    list_platforms_script.list_platforms_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    #Capture output
    out,err=capfd.readouterr()
    check_out = ["Combining yaml files", "model yaml", "platforms yaml"]
    for i in check_out:
        if i in out:
            assert True
        else:
           assert False

def test_nocombinedyaml():
    ''' test intermediate combined yaml was cleaned '''
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml").exists() == False

# Test individual functions operating correctly: combine and clean
def test_correct_combine():
    ''' test that combined yaml includes necesary keys '''
    p = None
    t = None
    yamlfile = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Combine model / experiment
    list_platforms_script.quick_combine(yamlfile,p,t)
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml").exists()

    comb_yamlfile = f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml"
    with open(comb_yamlfile, 'r') as yf:
        y = yaml.load(yf,Loader=yaml.Loader)

    req_keys = ["name","platform","target","fre_properties","platforms"]
    for k in req_keys:
        if k in y.keys():
            assert True
        else:
            assert False

def test_yamlremove():
   ''' test intermediate combined yaml removed '''
   # Remove combined yaml file
   list_platforms_script.remove(f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml")

   assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/combined-{EXP_NAME}.yaml").exists() == False
