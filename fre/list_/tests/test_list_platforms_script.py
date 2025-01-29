"""
Test fre list exps
"""
import pytest
from pathlib import Path
from fre.list_ import list_platforms_script

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
YAMLFILE = "null_model.yaml"
BADYAMLFILE = "null_model_bad.yaml"

# yaml file checks
def test_modelyaml_exists():
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}").exists()

def test_compileyaml_exists():
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/compile.yaml").exists()

def test_platformyaml_exists():
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/platforms.yaml").exists()

def test_exp_list(capfd):
    ''' test list exps '''
    list_platforms_script.list_platforms_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    #Capture output
    out,err=capfd.readouterr()
    if "Platforms available" in out:
        assert True
    else:
       assert False

@pytest.mark.xfail()
def test_exps_list_badyaml():
    ''' test failure of list exps tool given a bad yaml file path '''
    list_platforms_script.list_platforms_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{BADYAMLFILE}")
