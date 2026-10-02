"""
Test fre list exps
"""
from pathlib import Path

import pytest

from fre.list_ import list_experiments_script
from fre.yamltools import helpers

# SET-UP
TEST_DIR = Path("fre/list_/tests/yamls")
YAMLFILE = "model.yaml"
EXP_NAME = "None"

# yaml file checks
def test_modelyaml_exists():
    ''' Test that model yaml exists '''
    assert Path(f"{TEST_DIR}/{YAMLFILE}").exists()

# Test whole tool
def test_exp_list(caplog):
    ''' Test fre list exps subtool '''
    list_experiments_script.list_experiments_subtool(f"{TEST_DIR}/{YAMLFILE}")

    # check the logging output
    check_out = [ 'Experiments found:',
                  '   - experiment1',
                  '   - experiment2' ]
    for i in check_out:
        assert i in caplog.text

    # make sure the level is INFO
    for record in caplog.records:
        if record.name.startswith("fre"):
            assert record.levelname == "INFO"

# Test validation
@pytest.mark.skip(
    reason='cannot validate with current schema at the moment. Current schemas include final '
    '"combined" schema to validate compile and pp information. Both of these "clean" the final '
    'yaml information for only what is needed. This final combined yaml info does not include the '
    '"experiments" section, which is the section being read and parsed for information'
)
def test_yamlvalidate():
    ''' Test yaml is being validated '''
    yamlfilepath = Path(f"{TEST_DIR}/{YAMLFILE}")

    # Combine model / experiment
    yml_dict = list_experiments_script.list_experiments_subtool(f"{TEST_DIR}/{YAMLFILE}")

    # Validate and capture output
    assert helpers.validate_yaml(yml_dict, VAL_SCHEMA)
