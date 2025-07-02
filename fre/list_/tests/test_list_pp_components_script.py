"""
Test fre list pp-comps
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_pp_components_script
from fre.yamltools import combine_yamls_script as cy
from fre.yamltools import helpers

# SET-UP
TEST_DIR = Path("fre/pp/tests")
AM5_EXAMPLE = Path("AM5_example")
MODEL_YAMLFILE = "am5.yaml"
PP_YAMLFILES = ["yaml_include/pp.c96_amip.yaml", "yaml_include/pp-test.c96_amip.yaml", "yaml_include/settings.yaml"]
EXP_NAME = "c96L65_am5f7b12r1_amip"
VAL_SCHEMA = Path("fre/gfdl_msd_schemas/FRE/fre_pp.json")
PLATFORM = "FOO"
TARGET = "BAR"

# yaml file checks
def test_modelyaml_exists():
    ''' Make sure model yaml exists '''
    assert Path(f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}").exists()

def test_ppyamls_exist():
    ''' Make sure pp yamls exist '''
    for pp_yaml in PP_YAMLFILES:
        assert Path(f"{TEST_DIR}/{AM5_EXAMPLE}/{pp_yaml}").exists()

# Test whole tool
def test_exp_list(caplog):
    ''' test list exps '''
    list_pp_components_script.list_ppcomps_subtool(f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}", EXP_NAME)

    # check the logging output
    check_out = [ 'Components to be post-processed:',
                  '   - atmos',
                  '   - atmos_scalar']

    for i in check_out:
        assert i in caplog.text
        
    # make sure the level is INFO
    for record in caplog.records:
        assert record.levelname == "INFO"

# Test validation
def test_yamlvalidate(caplog):
    ''' test yaml is being validated '''
    # Combine model / experiment
    list_pp_components_script.list_ppcomps_subtool(f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}", EXP_NAME)

    validate = ["Validating YAML information...",
                "     YAML dictionary VALID."]

    for i in validate:
        assert i in caplog.text

    for record in caplog.records:
        record.levelname == "INFO"

def test_yamlcontent_valid():
    ''' Test that yaml dictionary content is valid '''
    yamlfile_path = f"{TEST_DIR}/{AM5_EXAMPLE}/{MODEL_YAMLFILE}"

    # Combine model / experiment
    yml_dict = cy.consolidate_yamls(yamlfile = yamlfile_path,
                                    experiment = EXP_NAME,
                                    platform = PLATFORM,
                                    target = TARGET,
                                    use = "pp",
                                    output = None) 

    expected_pp_comp_out_1 = {'type': 'atmos_cmip',
                              'sources': [{'history_file': 'atmos_month_cmip'}, {'history_file': 'atmos_8xdaily_cmip'}, {'history_file': 'atmos_daily_cmip'}],
                              'sourceGrid': 'cubedsphere',
                              'xyInterp': '180,360',
                              'interpMethod': 'conserve_order2',
                              'inputRealm': 'atmos',
                              'postprocess_on': False}
    expected_pp_comp_out_2 = {'type': 'atmos',
                              'sources': [{'history_file': 'atmos_month'}],
                              'sourceGrid': 'cubedsphere',
                              'xyInterp': '180,288',
                              'interpMethod': 'conserve_order2',
                              'inputRealm': 'atmos',
                              'postprocess_on': True}
    expected_pp_comp_out_3 = {'type': 'atmos_scalar',
                              'sources': [{'history_file': 'atmos_scalar'}],
                              'postprocess_on': True}
    expected_pp_comp_out_4 = {'type': 'aerosol_cmip',
                               'xyInterp': '180,288',
                               'sources': [{'history_file': 'aerosol_month_cmip'}],
                               'sourceGrid': 'cubedsphere',
                               'interpMethod': 'conserve_order1',
                               'inputRealm': 'atmos',
                               'postprocess_on': False}

    for key,value in yml_dict.items():
        if key == "components":
            assert expected_pp_comp_out_1 in value
            assert expected_pp_comp_out_2 in value
            assert expected_pp_comp_out_3 in value
            assert expected_pp_comp_out_4 in value
