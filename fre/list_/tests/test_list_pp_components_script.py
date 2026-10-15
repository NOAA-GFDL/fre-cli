"""
Test fre list pp-comps
"""
from pathlib import Path
from fre.list_ import list_pp_components_script


# SET-UP
#TEST_DIR = Path("fre/pp/tests")
TEST_DIR = Path("fre/list_/tests/yamls")
#AM5_EXAMPLE = Path("AM5_example")
MODEL_YAMLFILE = "model.yaml"
SETTINGS_YAMLFILE = "yaml_include/settings.yaml"
PP_YAMLFILES = ["yaml_include/pp.c96_amip.yaml", "yaml_include/pp-test.c96_amip.yaml"] #, "yaml_include/settings.yaml"]
EXP_NAME = "experiment1"
VAL_SCHEMA = Path("fre/gfdl_msd_schemas/FRE/fre_pp.json")
PLATFORM = "FOO"
TARGET = "BAR"

# yaml file checks
def test_modelyaml_exists():
    ''' Test model yaml exists '''
    assert Path(f"{TEST_DIR}/{MODEL_YAMLFILE}").exists()

def test_settingsyaml_exist():
    ''' Test settings yaml exists '''
    assert Path(f"{TEST_DIR}/{SETTINGS_YAMLFILE}").exists()

def test_ppyamls_exist():
    ''' Test post-processing yamls exist '''
    for pp_yaml in PP_YAMLFILES:
        assert Path(f"{TEST_DIR}/{pp_yaml}").exists()

# Test whole tool
def test_pp_comp_list(caplog):
    ''' Test fre list pp-components subtool '''
    list_pp_components_script.list_ppcomps_subtool(yamlfile = f"{TEST_DIR}/{MODEL_YAMLFILE}",
                                                   experiment = EXP_NAME,
                                                   application = "postprocess")

    # check the logging output
    check_out = [ 'Components to be post-processed:',
                  '   - atmos_cmip',
                  '   - atmos',
                  '   - atmos_diurnal',
                  '   - atmos_scalar',
                  '   - atmos_cmip-TEST' ]
    for i in check_out:
        assert i in caplog.text
    # make sure the level is WARNING for version mismatch and INFO otherwise
    for record in caplog.records:
        if record.name.startswith("fre"):
            assert record.levelname in ["WARNING", "INFO"]

# Test validation
def test_yamlvalidate(caplog):
    ''' Test yaml is being validated '''
    # Combine model / experiment
    list_pp_components_script.list_ppcomps_subtool(yamlfile = f"{TEST_DIR}/{MODEL_YAMLFILE}",
                                                   experiment = EXP_NAME,
                                                   application = "postprocess")

    validate = ["Validating YAML information...",
                "     YAML dictionary VALID."]

    for i in validate:
        assert i in caplog.text

    for record in caplog.records:
        if record.name.startswith("fre"):
            assert record.levelname in ["WARNING", "INFO"]
