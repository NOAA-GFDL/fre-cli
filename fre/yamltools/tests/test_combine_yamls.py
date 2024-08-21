import os
from pathlib import Path
import pytest
from fre.yamltools import combine_yamls as cy

## SET-UP
# Set example yaml paths, input directory
CWD = Path.cwd()
yamls_dir = Path("fre/yamltools/tests/AM5_example")
in_dir = Path(f"{CWD}/{yamls_dir}")

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
    os.chdir(in_dir)

    modelyaml = Path(f"{CWD}/{yamls_dir}/am5.yaml")

    cy._consolidate_yamls(modelyaml,EXPERIMENT, PLATFORM, TARGET)

    assert Path(f"{CWD}/{yamls_dir}/combined-c96L65_am5f7b12r1_amip.yaml").exists()
