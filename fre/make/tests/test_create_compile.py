"""
Test fre make compile-script
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
    # Set environment variable for use in ci.gnu platform
    os.environ["TEST_BUILD_DIR"] = OUT

    plat = PLATFORM[0]
    targ = TARGET[0]
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = PLATFORM,
                                         target = TARGET,
                                         jobs = 4,
                                         parallel = 1,
                                         execute = False,
                                         verbose = False)
    # Check for creation of compile script
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/compile.sh").exists()

def test_compile_executable_failure():
    """
    Check for the failure in execution of the compile script.
    Fails because it would need the makefile and checked out
    source code.
    """
    # Set environment variable for use in ci.gnu platform
    os.environ["TEST_BUILD_DIR"] = OUT

    plat = PLATFORM[0]
    targ = TARGET[0]
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Execute the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = PLATFORM,
                                         target = TARGET,
                                         jobs = 4,
                                         parallel = 1,
                                         execute = True,
                                         verbose = False)

    # Check for creation of compile script, FMS directory,
    # log.compile file, the executable
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/compile.sh").exists()
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/FMS").is_dir()
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/log.compile").exists()
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/null_model_full.x").exists() == False

@pytest.mark.xfail(raises=ValueError)
def test_bad_platform():
    """
    Check for the failure of compile script creation
    due to a bad platform passed.
    """
    # Set environment variable for use in ci.gnu platform
    os.environ["TEST_BUILD_DIR"] = OUT

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = BAD_PLATFORM,
                                         target = TARGET,
                                         jobs = 4,
                                         parallel = 1,
                                         execute = False,
                                         verbose = False)

def test_bad_platform_compilelog():
    """
    Check that compile log still created from the failure 
    of compile script creation due to a bad platform passed.
    """
    # Set environment variable for use in ci.gnu platform
    os.environ["TEST_BUILD_DIR"] = OUT

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    try:
        # Create the compile script
        create_compile_script.compile_create(yamlfile = yamlfile_path,
                                             platform = BAD_PLATFORM,
                                             target = TARGET,
                                             jobs = 4,
                                             parallel = 1,
                                             execute = False,
                                             verbose = False)
    except:
        assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{BAD_PLATFORM}-{TARGET}/exec/log.compile")

@pytest.mark.xfail(raises=ValueError)
def test_bad_target():
    """
    Check for the failure of compile script creation
    due to a bad target passed.
    """
    # Set environment variable for use in ci.gnu platform
    os.environ["TEST_BUILD_DIR"] = OUT

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = PLATFORM,
                                         target = BAD_TARGET,
                                         jobs = 4,
                                         parallel = 1,
                                         execute = False,
                                         verbose = False)

def test_bad_target_compilelog():
    """
    Check that compile log still created from the failure
    of compile script creation due to a bad target passed.
    """
    # Set environment variable for use in ci.gnu platform
    os.environ["TEST_BUILD_DIR"] = OUT

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    try:
        # Create the compile script
        create_compile_script.compile_create(yamlfile = yamlfile_path,
                                             platform = PLATFORM,
                                             target = BAD_TARGET,
                                             jobs = 4,
                                             parallel = 1,
                                             execute = False,
                                             verbose = False)
    except:
        assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{BAD_PLATFORM}-{TARGET}/exec/log.compile")

def test_multi_target():
    """
    Check for the creation of the compile script for each target passed
    """
    # Set environment variable for use in ci.gnu platform
    os.environ["TEST_BUILD_DIR"] = OUT

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = PLATFORM,
                                         target = MULTI_TARGET,
                                         jobs = 4,
                                         parallel = 1,
                                         execute = False,
                                         verbose = False)

    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{PLATFORM[0]}-{MULTI_TARGET[0]}/exec/compile.sh").exists()
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{PLATFORM[0]}-{MULTI_TARGET[1]}/exec/compile.sh").exists()
