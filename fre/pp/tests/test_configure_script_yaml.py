"""
Test configure_script_yaml
"""
import os
import shutil
from pathlib import Path
from fre.pp import configure_script_yaml as csy

# Set what would be click options
EXPERIMENT = "c96L65_am5f7b12r1_amip"
PLATFORM = "gfdl.ncrc5-intel22-classic"
TARGET = "prod-openmp"

# Set example yaml paths, input directory
TEST_DIR = Path("fre/pp/tests")
TEST_YAML = Path("AM5_example/am5.yaml")

def test_combinedyaml_exists():
    """
    Make sure combined yaml file exists
    """
    assert Path(f"{TEST_DIR}/{TEST_YAML}").exists()

def test_configure_script():
    """
    Tests success of confgure yaml script
    Creates rose-suite, regrid rose-app, remap rose-app
    TO-DO: will break this up for better tests
    """
    # Set home for ~/cylc-src location in script
    old_home = os.environ["HOME"]
    os.environ["HOME"] = str(Path(f"{TEST_DIR}/configure_yaml_out"))

    # Set output directory
    OUT_DIR = Path(f"{os.getenv('HOME')}/cylc-src/{EXPERIMENT}__{PLATFORM}__{TARGET}")
    Path(OUT_DIR).mkdir(parents = True, exist_ok = True)

    # Define combined yaml
    model_yaml = str(Path(f"{TEST_DIR}/{TEST_YAML}"))

    # Invoke configure_yaml_script.py
    csy.yaml_info(model_yaml, EXPERIMENT, PLATFORM, TARGET)

    os.environ["HOME"] = old_home

    # Check for configuration creation and final combined yaml
    assert all([ Path(f"{OUT_DIR}/{EXPERIMENT}.yaml"),
                 Path(f"{OUT_DIR}/rose-suite.conf").exists(),
                 Path(f"{OUT_DIR}/app/regrid-xy/rose-app.conf").exists(),
                 Path(f"{OUT_DIR}/app/remap-pp-components/rose-app.conf").exists() ])

def test_cleanup():
    shutil.rmtree(f"{TEST_DIR}/configure_yaml_out")
    assert not Path(f"{TEST_DIR}/configure_yaml_out").exists()
