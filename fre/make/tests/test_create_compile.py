"""
Test fre make compile-script
"""
import shutil
from pathlib import Path

import pytest

from fre.make import create_compile_script


## SET-UP — use __file__ so tests work from any working directory
TEST_DIR = Path(__file__).resolve().parent
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

# Output location
OUT = f"{TEST_DIR}/compile_out"

@pytest.fixture(autouse=True, scope="module")
def setup_compile_out():
    """Create a clean compile output directory for this test module."""
    if Path(OUT).exists():
        shutil.rmtree(OUT)
    Path(OUT).mkdir(parents=True, exist_ok=True)
    yield

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

def test_compile_creation(monkeypatch):
    """
    Check for the creation of the compile script
    """
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    plat = PLATFORM[0]
    targ = TARGET[0]
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = PLATFORM,
                                         target = TARGET,
                                         makejobs = 4,
                                         nparallel = 1,
                                         execute = False,
                                         verbose = False)
    # Check for creation of compile script
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/compile.sh").exists()

def test_compile_executable_failure(monkeypatch):
    """
    Check for the failure in execution of the compile script.
    Fails because it would need the makefile and checked out
    source code.
    """
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    plat = PLATFORM[0]
    targ = TARGET[0]
    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Execute the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = PLATFORM,
                                         target = TARGET,
                                         makejobs = 4,
                                         nparallel = 1,
                                         execute = True,
                                         verbose = False)

    # Check for creation of compile script, FMS directory,
    # log.compile file, the executable
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/compile.sh").exists()
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/FMS").is_dir()
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/log.compile").exists()
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{plat}-{targ}/exec/null_model_full.x").exists() == False

@pytest.mark.xfail(raises=ValueError)
def test_bad_platform(monkeypatch):
    """
    Check for the failure of compile script creation
    due to a bad platform passed.
    """
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = BAD_PLATFORM,
                                         target = TARGET,
                                         makejobs = 4,
                                         nparallel = 1,
                                         execute = False,
                                         verbose = False)

def test_bad_platform_compilelog(monkeypatch):
    """
    Check that compile log still created from the failure 
    of compile script creation due to a bad platform passed.
    """
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    try:
        # Create the compile script
        create_compile_script.compile_create(yamlfile = yamlfile_path,
                                             platform = BAD_PLATFORM,
                                             target = TARGET,
                                             makejobs = 4,
                                             nparallel = 1,
                                             execute = False,
                                             verbose = False)
    except:
        assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{BAD_PLATFORM}-{TARGET}/exec/log.compile")

@pytest.mark.xfail(raises=ValueError)
def test_bad_target(monkeypatch):
    """
    Check for the failure of compile script creation
    due to a bad target passed.
    """
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = PLATFORM,
                                         target = BAD_TARGET,
                                         makejobs = 4,
                                         nparallel = 1,
                                         execute = False,
                                         verbose = False)

def test_bad_target_compilelog(monkeypatch):
    """
    Check that compile log still created from the failure
    of compile script creation due to a bad target passed.
    """
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    try:
        # Create the compile script
        create_compile_script.compile_create(yamlfile = yamlfile_path,
                                             platform = PLATFORM,
                                             target = BAD_TARGET,
                                             makejobs = 4,
                                             nparallel = 1,
                                             execute = False,
                                             verbose = False)
    except:
        assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{BAD_PLATFORM}-{TARGET}/exec/log.compile")

def test_multi_target(monkeypatch):
    """
    Check for the creation of the compile script for each target passed
    """
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    yamlfile_path = f"{TEST_DIR}/{NM_EXAMPLE}/{YAMLFILE}"

    # Create the compile script
    create_compile_script.compile_create(yamlfile = yamlfile_path,
                                         platform = PLATFORM,
                                         target = MULTI_TARGET,
                                         makejobs = 4,
                                         nparallel = 1,
                                         execute = False,
                                         verbose = False)

    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{PLATFORM[0]}-{MULTI_TARGET[0]}/exec/compile.sh").exists()
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/{PLATFORM[0]}-{MULTI_TARGET[1]}/exec/compile.sh").exists()
