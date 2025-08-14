from pathlib import Path
import yaml
import pytest
from fre.app import helpers

## Path to example test data
DATA_DIR = Path("fre/app/remap_pp_components/tests/test-data")
## YAML configuration example file
YAML_EX = f"{DATA_DIR}/yaml_ex.yaml"

DIR_CHANGE = Path("fre/app/remap_pp_components")

def test_get_variables():
    """
    Test dictionary output with {source name: [variables]}
    from given pp component. 
    """
    # Load the yaml config
    with open(YAML_EX,'r') as f:
        yml=yaml.safe_load(f)

    expected_dicts = [{'atmos_scalar_test_vars': ['co2mass'],
                      'atmos_static_scalar_test_vars': ['bk']},

                      {'atmos_scalar_test_vars_fail': ['co2mass', 'bk', 'no_var']},

                      {'atmos_scalar_static_test_vars_fail2': 'all',
                      'atmos_static_scalar_test_vars_fail': ['bk', 'no_var']}]

    components = ["atmos_scalar_test_vars", "atmos_scalar_test_vars_fail", "atmos_scalar_static_test_vars_fail"]

    out1 = helpers.get_variables(yml = yml, pp_comp = components[0])
    out2 = helpers.get_variables(yml = yml, pp_comp = components[1])
    out3 = helpers.get_variables(yml = yml, pp_comp = components[2])

    assert all([len(out1) !=0,
                len(out2) !=0,
                len(out3) !=0,
                out1 == expected_dicts[0],
                out2 == expected_dicts[1],
                out3 == expected_dicts[2]])
             
def test_get_variables_err():
    """
    Test get_variables() returns an error when given inappropriate input
    """
    with pytest.raises( TypeError ) as execinfo:
        out = helpers.get_variables(yml = YAML_EX, pp_comp = "test_param")
    assert execinfo.type is TypeError

def test_change_directory():
    """
    Test change_directory context manager.
    This allows for the changing of directories within
    a function's execution. 
    After execution of the function, user should be in 
    the same directory the script started in.
    """
    original_dir = Path.cwd()

    with helpers.change_directory(DIR_CHANGE):
        new_dir = Path.cwd()

    final_dir = Path.cwd()

    assert all([original_dir == final_dir,
                original_dir != new_dir,
                new_dir != final_dir])
