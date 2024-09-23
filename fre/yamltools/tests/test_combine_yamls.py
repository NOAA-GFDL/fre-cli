import os
from pathlib import Path
import pytest
import shutil
import json
import yaml
from jsonschema import validate, ValidationError, SchemaError
from fre.yamltools import combine_yamls as cy
from multiprocessing import Process


## SET-UP
# Set example yaml paths, input directory, output directory
CWD = Path.cwd()
test_dir = Path("fre/yamltools/tests")
in_dir = Path(f"{CWD}/{test_dir}/AM5_example")

# Create output directories
comp_out_dir = Path(f"{CWD}/{test_dir}/combine_yamls_out/compile")
pp_out_dir = Path(f"{CWD}/{test_dir}/combine_yamls_out/pp")

# If output directory exists, remove and create again 
for out in [comp_out_dir, pp_out_dir]:
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
    assert Path(f"{in_dir}/am5.yaml").exists()

def test_compileyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{in_dir}/compile_yamls/compile.yaml").exists()

def test_platformyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{in_dir}/compile_yamls/platforms.yaml").exists()

def test_merged_compile_yamls():
    """
    Check for the creation of the combined-[experiment] yaml 
    Check that the model yaml was merged into the combined yaml
    """
    # Go into the input directory
    os.chdir(in_dir)

    # Model yaml path
    modelyaml = "am5.yaml"
    USE = "compile"

    # Merge the yamls
    cy._consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, USE)

    # Move combined yaml to output location
    shutil.move(f"combined-am5.yaml", comp_out_dir)

    # Check that the combined yaml exists
    assert Path(f"{comp_out_dir}/combined-{COMP_EXPERIMENT}.yaml").exists()

def test_combined_compileyaml_validation():
    """
    Validate the combined compile yaml
    """
    combined_yamlfile =f"{comp_out_dir}/combined-{COMP_EXPERIMENT}.yaml"
    schema_file = os.path.join(f"{in_dir}","compile_yamls","schema.json")

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
    # Go into the input directory
    os.chdir(f"{in_dir}/compile_yamls/compile_fail")

    # Model yaml path
    modelyaml = f"am5-wrong_compilefile.yaml"
    USE = "compile"

    # Merge the yamls - should fail since there is no compile yaml specified in the model yaml
    try:
        consolidate = cy._consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, USE)
        # Move combined yaml to output location
        shutil.move(f"combined-am5-wrong_compilefile.yaml", comp_out_dir)
    except:
        print("EXPECTED FAILURE")
        # Move combined yaml to output location
        shutil.move(f"combined-am5-wrong_compilefile.yaml", comp_out_dir)
        assert True

def test_combined_compileyaml_validatefail():
    """
    Check if the schema is validating correctly
    Branch should be string
    """
    # Go into the input directory
    os.chdir(f"{in_dir}/compile_yamls/compile_fail")

    # Model yaml path
    modelyaml = "am5-wrong_datatype.yaml"
    USE = "compile"

    # Merge the yamls
    cy._consolidate_yamls(modelyaml, COMP_EXPERIMENT, COMP_PLATFORM, COMP_TARGET, USE)

    # Move combined yaml to output location
    shutil.move(f"combined-am5-wrong_datatype.yaml", comp_out_dir)

    # Validate against schema; should fail
    wrong_combined = Path(f"{comp_out_dir}/combined-am5-wrong_datatype.yaml")     
    schema_file = os.path.join(f"{in_dir}","compile_yamls","schema.json")

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
    assert Path(f"{in_dir}/pp_yamls/pp.c96_amip.yaml").exists()

@pytest.mark.skip(reason='analysis scripts might not be defined yet')
def test_analysisyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{in_dir}/pp_yamls/analysis.yaml").exists()

def test_merged_pp_yamls():
    """
    Check for the creation of the combined-[experiment] yaml
    Check that the model yaml was merged into the combined yaml
    """
    # Go into the input directory
    os.chdir(in_dir)

    # Model yaml path
    modelyaml = Path(f"{in_dir}/am5.yaml")
    USE = "pp"

    # Merge the yamls
    cy._consolidate_yamls(modelyaml, PP_EXPERIMENT, PP_PLATFORM, PP_TARGET, USE)

    # Move combined yaml to output location
    shutil.move(f"combined-{PP_EXPERIMENT}.yaml", pp_out_dir)

    # Check that the combined yaml exists
    assert Path(f"{pp_out_dir}/combined-{PP_EXPERIMENT}.yaml").exists()

def test_combined_ppyaml_validation():
    """
    Validate the combined compile yaml
    """
    combined_yamlfile =f"{pp_out_dir}/combined-{PP_EXPERIMENT}.yaml"
    schema_dir = Path(f"{in_dir}/pp_yamls")
    schema_file = os.path.join(schema_dir, 'schema.json')

    with open(combined_yamlfile,'r') as cf:
        yml = yaml.safe_load(cf)

    with open(schema_file,'r') as f:
        s = f.read()
    schema = json.loads(s)

    validate(instance=yml,schema=schema)
