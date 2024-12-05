"""
Test fre make create-compile
"""
import os
import shutil
from pathlib import Path
from fre.make import create_compile_script

# SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
YAMLFILE = "null_model.yaml"
PLATFORM = ["ncrc5.intel23"]
TARGET = ["debug"]
EXPERIMENT = "null_model_full"

# Create output location
OUT = f"{TEST_DIR}/compile_out"
if Path(OUT).exists():
    # remove
    shutil.rmtree(OUT)
    # create output directory
    Path(OUT).mkdir(parents=True,exist_ok=True)
else:
    Path(OUT).mkdir(parents=True,exist_ok=True)

def test_modelyaml_exists():
    """
    Check the model yaml exists
    """
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}").exists()

def test_compileyaml_exists():
    """
    Check the compile yaml exists
    """
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/compile.yaml").exists()

def test_platformyaml_exists():
    """
    Check the platform yaml exists
    """
    assert Path(f"{TEST_DIR}/{NM_EXAMPLE}/platforms.yaml").exists()

def test_compile_creation():
    """
    Check for the creation of the compile script
    """
    # Save default HOME location
    def_home = str(os.environ["HOME"])
    # Change HOME for compile script output
    os.environ["HOME"]=OUT

    plat = PLATFORM[0]
    targ = TARGET[0]
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile_path, PLATFORM, TARGET, 4, 1, False, False)

    # Set HOME back to default
    os.environ["HOME"] = def_home

    # Check for creation of compile script
    # Check for correct default HOME location set
    assert [Path(f"{OUT}/fremake_Canopy/test/null_model_full/{plat}-{targ}/exec/compile.sh").exists(),
            os.environ["HOME"] == def_home]

def test_compile_execution():
    """
    Check for the successful execution of the compile script
    """
    # Save default HOME location
    def_home = str(os.environ["HOME"])
    # Change HOME for compile script output
    os.environ["HOME"]=OUT

    plat = PLATFORM[0]
    targ = TARGET[0]
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Execute the compile script
    create_compile_script.compile_create(yamlfile_path, PLATFORM, TARGET, 4, 1, True, False)

    # Set HOME back to default
    os.environ["HOME"] = def_home

    # Check for creation of compile script
    # Check for FMS directory
    # Check for log.compile file
    # Check for correct default HOME location set
    assert [Path(f"{OUT}/fremake_Canopy/test/null_model_full/{plat}-{targ}/exec/compile.sh").exists(),
            Path(f"{OUT}/fremake_Canopy/test/null_model_full/{plat}-{targ}/exec/FMS").is_dir(),
            Path(f"{OUT}/fremake_Canopy/test/null_model_full/{plat}-{targ}/exec/log.compile"),
            os.environ["HOME"] == def_home]

#TO-DO: check for failures, ETC....
