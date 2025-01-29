"""
Test fre list exps
"""
import pytest
from pathlib import Path
from fre.list_ import list_experiments_script

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
YAMLFILE = "null_model.yaml"
BADYAMLFILE = "null_model_bad.yaml"

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

@pytest.mark.xfail()
def test_exps_list_badyaml():
    ''' test failure of list exps tool given a bad yaml file path '''
    list_experiments_script.list_experiments_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{BADYAMLFILE}")
