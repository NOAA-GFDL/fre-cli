"""
Test fre list platforms
"""
import pytest
from pathlib import Path
import yaml
from fre.list_ import list_platforms_script
from fre.yamltools import combine_yamls_script as cy

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
PLATFORM = None
TARGET = None
YAMLFILE = "null_model.yaml"
EXP_NAME = YAMLFILE.split(".")[0]
VAL_SCHEMA = Path("fre/gfdl_msd_schemas/FRE/fre_make.json")

# Bad yaml example
BADYAMLFILE_PATH = f"{TEST_DIR}/{NM_EXAMPLE}/wrong_model/wrong_null_model.yaml"


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

# Test whole tool 
def test_platforms_list_correct(caplog):
    ''' test list platforms '''
    list_platforms_script.list_platforms_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    # check the logging output
    check_out = ["Platforms available:",
                 "    - ncrc5.intel23",
                 "    - hpcme.2023",
                 "    - ci.gnu",
                 "    - con.twostep"    ]
    for i in check_out:
        assert i in caplog.text

    # make sure level is INFO
    for record in caplog.records:
        record.levelname == "INFO"

# Test validation
def test_yamlvalidate(caplog):
    ''' Test yaml is being validated and is actually valid'''
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Combine model / experiment
    list_platforms_script.list_platforms_subtool(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}")

    validate = ["Validating YAML information...",
                "     YAML dictionary VALID."]

    for i in validate:
        assert i in caplog.text

    for record in caplog.records:
        record.levelname == "INFO"

def test_check_expected_yamlcontent():
    ''' Test that expected yaml information is included in dictionary content '''
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Combine model / experiment
    yml_dict = cy.consolidate_yamls(yamlfile = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}",
                                    experiment = EXP_NAME,
                                    platform = PLATFORM,
                                    target = TARGET,
                                    use = "compile",
                                    output = None)

    # compare combined yaml info with some information that's supposed to be parsed
    expected_platform_info_1 = {'name': 'ncrc5.intel23',
                                'compiler': 'intel',
                                'modulesInit': [' module use -a /ncrc/home2/fms/local/modulefiles \n', 'source $MODULESHOME/init/sh \n'],
                                'modules': ['intel-classic/2023.2.0', 'fre/bronx-21', 'cray-hdf5/1.12.2.11', 'cray-netcdf/4.9.0.11'],
                                'mkTemplate': '/ncrc/home2/fms/local/opt/fre-commands/bronx-20/site/ncrc5/intel-classic.mk',
                                'modelRoot': '${HOME}/fremake_canopy/test'}
    expected_platform_info_2 = {'name': 'hpcme.2023',
                                'compiler': 'intel',
                                'RUNenv': ['. /spack/share/spack/setup-env.sh', 'spack load libyaml', 'spack load netcdf-fortran@4.5.4', 'spack load hdf5@1.14.0'],
                                'modelRoot': '/apps',
                                'container': True,
                                'containerBuild': 'podman',
                                'containerRun': 'apptainer',
                                'containerBase': 'docker.io/ecpe4s/noaa-intel-prototype:2023.09.25',
                                'mkTemplate': '/apps/mkmf/templates/hpcme-intel21.mk'}

    for key,value in yml_dict.items():
        if key == "platforms":
            assert expected_platform_info_1 in value
            assert expected_platform_info_2 in value

@pytest.mark.xfail
def test_not_valid_yaml():
    ''' Test correct output when yaml is invalid '''
    # Combine model / experiment
    list_platforms_script.list_platforms_subtool(f"{BADYAMLFILE_PATH}")

    validate = ["Validating YAML information...",
                "     YAML dictionary NOT VALID."]

    for i in validate:
        assert i in caplog.text

    for record in caplog.records:
        record.levelname == "INFO"
