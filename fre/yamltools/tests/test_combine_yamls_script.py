"""
tests routines in fre.yamltools.combine_yamls
"""
import os
from pathlib import Path
import pytest
import shutil
import json
import yaml
import pprint
from jsonschema import validate
from fre.yamltools import combine_yamls_script as cy


## SET-UP
# Set example yaml paths, input directory, output directory
#CWD = Path.cwd()
TEST_DIR = Path("fre/yamltools/tests")
IN_DIR = Path(f"{TEST_DIR}/AM5_example")
SCHEMA_DIR = Path("fre/gfdl_msd_schemas/FRE")

# Create output directories
COMP_OUT_DIR = Path(f"{TEST_DIR}/combine_yamls_out/compile")
PP_OUT_DIR = Path(f"{TEST_DIR}/combine_yamls_out/pp")

# If output directory exists, remove and create again
for outdir in [COMP_OUT_DIR, PP_OUT_DIR]:
    if outdir.exists():
        shutil.rmtree(outdir)
        Path(outdir).mkdir(parents=True,exist_ok=True)
    else:
        Path(outdir).mkdir(parents=True,exist_ok=True)

## Set what would be click options
# Compile
COMP_EXPERIMENT = "am5"
COMP_PLATFORM = "ncrc5.intel23"
COMP_TARGET = "prod"

# Post-processing
PP_EXPERIMENT = "c96L65_am5f7b12r1_amip"
PP_PLATFORM = "gfdl.ncrc5-intel22-classic"
PP_TARGET = "prod"

def test_modelyaml_exists():
    """
    Make sure main yaml file exists
    """
    assert Path(f"{IN_DIR}/am5.yaml").exists()

def test_compileyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{IN_DIR}/compile_yamls/compile.yaml").exists()

def test_platformyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{IN_DIR}/compile_yamls/platforms.yaml").exists()

def test_merged_compile_yamls():
    """
    Check for the creation of the combined-[experiment] yaml
    Check that the model yaml was merged into the combined yaml
    """
    # Model yaml path
    modelyaml = str(Path(f"{IN_DIR}/am5.yaml"))
    use = "compile"

    # Merge the yamls
    try:
        cy.consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, use, output = None)
    except:
        assert False

def test_combined_compileyaml_validation():
    """
    Validate the combined compile yaml
    """
    # Model yaml path
    modelyaml = str(Path(f"{IN_DIR}/am5.yaml"))
    use = "compile"

    # Merge the yamls
    try:
        out = cy.consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, use, output = None)
    except:
        assert False

    schema_file = os.path.join(SCHEMA_DIR, "fre_make.json")
    with open(schema_file,'r') as f:
        s = f.read()
    schema = json.loads(s)

    # If the yaml is valid, no issues
    # If the yaml is not valid, error
    try:
        validate(instance=out,schema=schema)
    except:
        assert False

def test_combined_compileyaml_combinefail():
    """
    Check to test if compile yaml is incorrect/does not exist,
    the combine fails. (compile yaml path misspelled)
    """
    # Model yaml path
    modelyaml = str(Path(f"{IN_DIR}/compile_yamls/compile_fail/am5-wrong_compilefile.yaml"))
    use = "compile"

    # Merge the yamls - should fail since there is no compile yaml specified in the model yaml
    try:
        #out =
        cy.consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, use, output = None)
    except:
        print("EXPECTED FAILURE")
        assert True

def test_combined_compileyaml_validatefail():
    """
    Check if the schema is validating correctly
    Branch should be string
    """
    # Model yaml path
    modelyaml = str(Path(f"{IN_DIR}/compile_yamls/compile_fail/am5-wrong_datatype.yaml"))
    use = "compile"

    # Merge the yamls
    try:
        out = cy.consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, use, output = None)
    except:
        assert False

    # Validate against schema; should fail
    schema_file = os.path.join(SCHEMA_DIR, "fre_make.json")

    # Open/load schema.jaon
    with open(schema_file,'r') as f:
        s = f.read()
    schema = json.loads(s)

    # Validation should fail
    try:
        validate(instance=out,schema=schema)
    except:
        assert True

def test_check_expected_platformyamlcontent():
    ''' Test that expected yaml information (platform info) is included in dictionary content '''
    TEST_DIR = Path("fre/make/tests")
    NM_EXAMPLE = Path("null_example")
    YAMLFILE = "null_model.yaml"
    EXP_NAME = YAMLFILE.split(".")[0]

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Combine model / experiment
    yml_dict = cy.consolidate_yamls(yamlfile = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}",
                                    experiment = EXP_NAME,
                                    platform = None,
                                    target = None,
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

############ PP ############
def test_expyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{IN_DIR}/pp_yamls/pp.c96_amip.yaml").exists()

@pytest.mark.skip(reason='analysis scripts might not be defined yet')
def test_analysisyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{IN_DIR}/pp_yamls/analysis.yaml").exists()

def test_merged_pp_yamls():
    """
    Check for the creation of the combined-[experiment] yaml
    Check that the model yaml was merged into the combined yaml
    """
    # Model yaml path
    modelyaml = Path(f"{IN_DIR}/am5.yaml")
    use = "pp"

    # Merge the yamls
    try:
        cy.consolidate_yamls(modelyaml, PP_EXPERIMENT, PP_PLATFORM, PP_TARGET, use, output=None)
    except:
        assert False

def test_combined_ppyaml_validation():
    """
    Validate the combined compile yaml
    """
    modelyaml = Path(f"{IN_DIR}/am5.yaml")
    use = 'pp'

    # Merge the yamls
    try:
        out = cy.consolidate_yamls(modelyaml, PP_EXPERIMENT, PP_PLATFORM, PP_TARGET, use, output=None)
    except:
        assert False

    schema_file = os.path.join(SCHEMA_DIR, "fre_pp.json")
    with open(schema_file,'r') as f:
        s = f.read()
    schema = json.loads(s)

    validate(instance=out,schema=schema)

def test_combine_pp_yamls(tmp_path):
    """
    Verify yaml combiner functionality by combining
    a model yaml with 3 pp yamls (2 with components).
    """

    model = {
        'experiments' : [
            {
                'name' : 'expname',
                'settings': 'settings.yaml',
                'pp'   : [
                    'pp1.yaml',
                    'pp2.yaml'
                ]
            }
        ]
    }

    settings = {
        'directories' : {
            'history_dir': 'one',
            'pp_dir'     : 'two'
        },
        'postprocess' : {
            'settings' : {
                'history_segment' : 'three',
                'pp_start'        : 'four'
            }
        }
    }

    pp1 = {
        'postprocess' : {
            'components' : [
                {
                    'type'    : 'atmos_cmip',
                    'sources' : "foo bar" },
                {
                    'type'    : 'land',
                    'sources' : "land_month"}
            ]
        }
    }

    pp2 = {
        'postprocess' : {
            'components' : [
                {
                    'type'    : 'ocean',
                    'sources' : "a b c" },
                {
                    'type'    : 'ice',
                    'sources' : "ice_month"}
            ]
        }
    }

    combined = {
        'name' : 'expname',
        'platform' : 'platform',
        'target' : 'target',
        'directories' : {
            'history_dir': 'one',
            'pp_dir'     : 'two'
        },
        'postprocess' : {
            'settings' : {
                'history_segment' : 'three',
                'pp_start'        : 'four'
            },
            'components' : [
                {
                    'type'    : 'atmos_cmip',
                    'sources' : "foo bar" },
                {
                    'type'    : 'land',
                    'sources' : "land_month"},
                {
                    'type'    : 'ocean',
                    'sources' : "a b c" },
                {
                    'type'    : 'ice',
                    'sources' : "ice_month"}
            ]
        }
    }

    # create temp directory
    tmp_path.mkdir(exist_ok=True)

    # create model and pp yamls
    file_model = open(tmp_path / 'model.yaml', 'w')
    file_settings = open(tmp_path / 'settings.yaml', 'w')
    file_pp1 = open(tmp_path / 'pp1.yaml', 'w')
    file_pp2 = open(tmp_path / 'pp2.yaml', 'w')

    # write to/ dump info into created model and pp yamls
    yaml.dump(model, file_model, default_flow_style=False, sort_keys=False)
    yaml.dump(settings, file_settings, default_flow_style=False, sort_keys=False)
    yaml.dump(pp1, file_pp1, default_flow_style=False, sort_keys=False)
    yaml.dump(pp2, file_pp2, default_flow_style=False, sort_keys=False)

    # combine the yamls
    # output is a combined dictionary of necessary yaml info
    output = cy.consolidate_yamls(tmp_path / 'model.yaml', 'expname', 'platform', 'target', 'pp', output=None)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(output)
    pp.pprint(combined)

    # compare dictionaries
    assert output == combined

def test_combine_cmor_yaml():
    """
    Verify yaml combiner functionality by combining
    a model yaml with a cmor yaml
    """
    output_combined_cmor_yaml = "fre/yamltools/tests/AM5_example/FOO_cmor.yaml"
    if Path(output_combined_cmor_yaml).exists():
        Path(output_combined_cmor_yaml).unlink()
    cy.consolidate_yamls( yamlfile = 'fre/yamltools/tests/AM5_example/am5.yaml',
                          experiment = 'c96L65_am5f7b12r1_amip',
                          platform = 'ncrc5.intel',
                          target = 'prod-openmp',
                          use = 'cmor',
                          output = output_combined_cmor_yaml )
    assert Path(output_combined_cmor_yaml).exists()

    compare_combined_cmor_yaml = "fre/yamltools/tests/AM5_example/COMPARE_TEST_OUTPUT_cmor.yaml"
    assert Path(compare_combined_cmor_yaml).exists()
    comp_file_output = open(compare_combined_cmor_yaml, 'r')
    comp_file_output_data = yaml.load(comp_file_output, Loader=yaml.SafeLoader)


    file_output = open(output_combined_cmor_yaml, 'r')
    file_output_data = yaml.load(file_output, Loader=yaml.SafeLoader)

    assert file_output_data == comp_file_output_data
