"""
tests routines in fre.yamltools.combine_yamls
"""
import os
from pathlib import Path
import pytest
import shutil
import json
import yaml
from jsonschema import validate
from fre.yamltools import combine_yamls as cy


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
for out in [COMP_OUT_DIR, PP_OUT_DIR]:
    if out.exists():
        shutil.rmtree(out)
        Path(out).mkdir(parents=True,exist_ok=True)
    else:
        Path(out).mkdir(parents=True,exist_ok=True)

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
    cy.consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, use)

    # Move combined yaml to output location
    shutil.move(f"{IN_DIR}/combined-am5.yaml", COMP_OUT_DIR)

    # Check that the combined yaml exists
    assert Path(f"{COMP_OUT_DIR}/combined-{COMP_EXPERIMENT}.yaml").exists()

def test_combined_compileyaml_validation():
    """
    Validate the combined compile yaml
    """
    combined_yamlfile =f"{COMP_OUT_DIR}/combined-{COMP_EXPERIMENT}.yaml"
    schema_file = os.path.join(SCHEMA_DIR, "fre_make.json")

    with open(combined_yamlfile,'r') as cf:
        yml = yaml.safe_load(cf)

    with open(schema_file,'r') as f:
        s = f.read()
    schema = json.loads(s)

    # If the yaml is valid, no issues
    # If the yaml is not valid, error
    try:
        validate(instance=yml,schema=schema)
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
        cy.consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, use)
        # Move combined yaml to output location
        shutil.move(f"{IN_DIR}/compile_yamls/compile_fail/combined-am5-wrong_compilefile.yaml", COMP_OUT_DIR)
    except:
        print("EXPECTED FAILURE")
        # Move combined yaml to output location
        shutil.move(f"{IN_DIR}/compile_yamls/compile_fail/combined-am5-wrong_compilefile.yaml", COMP_OUT_DIR)
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
    cy.consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, use)

    # Move combined yaml to output location
    shutil.move(f"{IN_DIR}/compile_yamls/compile_fail/combined-am5-wrong_datatype.yaml", COMP_OUT_DIR)

    # Validate against schema; should fail
    wrong_combined = Path(f"{COMP_OUT_DIR}/combined-am5-wrong_datatype.yaml")
    schema_file = os.path.join(SCHEMA_DIR, "fre_make.json")

    # Open/load combined yaml file
    with open(wrong_combined,'r') as cf:
        yml = yaml.safe_load(cf)

    # Open/load schema.jaon
    with open(schema_file,'r') as f:
        s = f.read()
    schema = json.loads(s)

    # Validation should fail
    try:
        validate(instance=yml,schema=schema)
    except:
        assert True

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
    cy.consolidate_yamls(modelyaml, PP_EXPERIMENT, PP_PLATFORM, PP_TARGET, use)

    # Move combined yaml to output location
    shutil.move(f"combined-{PP_EXPERIMENT}.yaml", PP_OUT_DIR)

    # Check that the combined yaml exists
    assert Path(f"{PP_OUT_DIR}/combined-{PP_EXPERIMENT}.yaml").exists()

def test_combined_ppyaml_validation():
    """
    Validate the combined compile yaml
    """
    combined_yamlfile =f"{PP_OUT_DIR}/combined-{PP_EXPERIMENT}.yaml"
    schema_dir = Path(f"{IN_DIR}/pp_yamls")
    schema_file = os.path.join(schema_dir, 'schema.json')

    with open(combined_yamlfile,'r') as cf:
        yml = yaml.safe_load(cf)

    with open(schema_file,'r') as f:
        s = f.read()
    schema = json.loads(s)

    validate(instance=yml,schema=schema)

def test_combine_pp_yamls(tmp_path):
    """
    Verify yaml combiner functionality by combining
    a model yaml with 3 pp yamls (2 with components).
    """

    model = {
        'experiments' : [
            {
                'name' : 'expname',
                'pp'   : [
                    'pp1.yaml',
                    'pp2.yaml',
                    'pp3.yaml'
                ]
            }
        ]
    }

    pp1 = {
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

    pp2 = {
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

    pp3 = {
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

    # write model and pp yamls
    file_model = open(tmp_path / 'model.yaml', 'w')
    file_pp1 = open(tmp_path / 'pp1.yaml', 'w')
    file_pp2 = open(tmp_path / 'pp2.yaml', 'w')
    file_pp3 = open(tmp_path / 'pp3.yaml', 'w')

    yaml.dump(model, file_model)
    yaml.dump(pp1, file_pp1)
    yaml.dump(pp2, file_pp2)
    yaml.dump(pp3, file_pp3)

    # combine the yamls
    # output file is 'combined-expname.yaml' in the current directory
    cy.consolidate_yamls(tmp_path / 'model.yaml', 'expname', 'platform', 'target', 'pp')

    # open the combined yaml and compare to expected reference
    file_output = open('combined-expname.yaml', 'r')
    output = yaml.load(file_output, Loader=yaml.SafeLoader)
    assert output == combined

    # remove combined yaml
    Path('combined-expname.yaml').unlink()
