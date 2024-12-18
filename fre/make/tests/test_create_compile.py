"""
Test fre make create-compile
"""
import os
import shutil
import pytest
from pathlib import Path
from fre.make import create_compile_script

## SET-UP
TEST_DIR = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
YAMLFILE = "null_model.yaml"
PLATFORM = ["ci.gnu"]
TARGET = ["debug"]
EXPERIMENT = "null_model_full"

# Multi-plat-targ
MULTI_TARGET = ["prod","repro"]

# Bad plat/targ
BAD_PLATFORM=["no_plat"]
BAD_TARGET=["no_targ"]

# Create output location
OUT = f"{TEST_DIR}/compile_out"
if Path(OUT).exists():
    # remove
    shutil.rmtree(OUT)
    # create output directory
    Path(OUT).mkdir(parents=True,exist_ok=True)
else:
    Path(OUT).mkdir(parents=True,exist_ok=True)

# Set environment variable for use in ci.gnu platform
os.environ["TEST_BUILD_DIR"] = OUT

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
    plat = PLATFORM[0]
    targ = TARGET[0]
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile_path, PLATFORM, TARGET, 4, 1, False, False)

    # Check for creation of compile script
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/compile.sh").exists()

def test_compile_execution():
    """
    Check for the successful execution of the compile script
    """
    plat = PLATFORM[0]
    targ = TARGET[0]
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Execute the compile script
    create_compile_script.compile_create(yamlfile_path, PLATFORM, TARGET, 4, 1, True, False)

    # Check for creation of compile script
    # Check for FMS directory
    # Check for log.compile file
    assert [Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/compile.sh").exists(),
            Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/FMS").is_dir(),
            Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/log.compile")]

@pytest.mark.xfail(raises=AttributeError)
def test_bad_platform():
    """
    Check for the failure of compile script creation
    due to a bad platform passed.
    """
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile_path, BAD_PLATFORM, TARGET, 4, 1, False, False)

def test_bad_platform_compilelog():
    """
    Check that compile log still created from the failure 
    of compile script creation due to a bad platform passed.
    """
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    try:
        # Create the compile script
        create_compile_script.compile_create(yamlfile_path, BAD_PLATFORM, TARGET, 4, 1, False, False)
    except:
        assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{BAD_PLATFORM}-{TARGET}/exec/log.compile")

@pytest.mark.xfail(raises=AttributeError)
def test_bad_target():
    """
    Check for the failure of compile script creation
    due to a bad target passed.
    """
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile_path, PLATFORM, BAD_TARGET, 4, 1, False, False)

def test_bad_target_compilelog():
    """
    Check that compile log still created from the failure
    of compile script creation due to a bad target passed.
    """
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    try:
        # Create the compile script
        create_compile_script.compile_create(yamlfile_path, PLATFORM, BAD_TARGET, 4, 1, False, False)
    except:
        assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{BAD_PLATFORM}-{TARGET}/exec/log.compile")

def test_multi_target():
    """
    Check for the creation of the compile script for each target passed
    """
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile_path, PLATFORM, MULTI_TARGET, 4, 1, False, False)

    for t in MULTI_TARGET:
        assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{PLATFORM[0]}-{t}/exec/compile.sh").exists()
