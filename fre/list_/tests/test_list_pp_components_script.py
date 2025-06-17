"""
Test fre list pp-comps
"""

import pytest
from pathlib import Path
import yaml
from fre.list_ import list_pp_components_script

# SET-UP
TEST_DIR = Path("fre/pp/tests")
AM5_EXAMPLE = Path("AM5_example")
YAMLFILE = "am5.yaml"
EXP_NAME = "c96L65_am5f7b12r1_amip"


# yaml file checks
def test_modelyaml_exists():
    """Make sure model yaml exists"""
    assert Path(f"{TEST_DIR}/{AM5_EXAMPLE}/{YAMLFILE}").exists()


def test_exp_list(caplog):
    """test list exps"""
    list_pp_components_script.list_ppcomps_subtool(f"{TEST_DIR}/{AM5_EXAMPLE}/{YAMLFILE}", EXP_NAME)

    # check the logging output
    check_out = ["Components to be post-processed:", "   - atmos", "   - atmos_scalar"]

    for i in check_out:
        assert i in caplog.text

    # make sure the level is INFO
    for record in caplog.records:
        assert record.levelname == "INFO"
