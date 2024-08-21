import os
from pathlib import Path
import pytest
import shutil
from fre.yamltools import combine_yamls as cy

## SET-UP
# Set example yaml paths, input directory, output directory
CWD = os.getcwd()
yamls_dir = Path("fre/yamltools/tests/AM5_example")
in_dir = Path(f"{CWD}/{yamls_dir}")

# Create output directory
out_dir = Path(f"{CWD}/fre/yamltools/tests/combine_yamls_out")

# If output directory exists, remove and create again 
if Path(out_dir).exists:
    shutil.rmtree(out_dir)
    Path(out_dir).mkdir(parents=True,exist_ok=True)
else:
    Path(out_dir).mkdir(parents=True,exist_ok=True)

# Set what would be click options
EXPERIMENT = "c96L65_am5f7b12r1_amip"
PLATFORM = "gfdl.ncrc5-intel22-classic"
TARGET = "prod"

def test_modelyaml_exists():
    """
    Make sure main yaml file exists
    """
    assert Path(f"{CWD}/{yamls_dir}/am5.yaml").exists()

def test_compileyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{CWD}/{yamls_dir}/compile.yaml").exists()

def test_platformyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{CWD}/{yamls_dir}/yaml_include/platforms.yaml").exists()

def test_expyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{CWD}/{yamls_dir}/yaml_include/pp.c96_amip.yaml").exists()

@pytest.mark.skip(reason='analysis scripts might not be defined')
def test_analysisyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{CWD}/{yamls_dir}/yaml_include/analysis.yaml").exists()

def test_merged_yamls():
    """
    Check for the creation of the combined-[experiment] yaml 
    Check that the model yaml was merged into the combined yaml
    """
    # Model yaml path
    modelyaml = Path(f"{in_dir}/am5.yaml")

    # Merge the yamls
    cy._consolidate_yamls(modelyaml,EXPERIMENT, PLATFORM, TARGET)

    # Move combined yaml to output location
    shutil.move(f"{CWD}/combined-{EXPERIMENT}.yaml", out_dir)

    # Check that the combined yaml exists
    assert Path(f"{out_dir}/combined-{EXPERIMENT}.yaml").exists()

##TO-DO:
# - check for correct yaml merging
# - 
