''' this file holds any run-fremake tests that actually compile the model code
 these tests assume your os is the ci image (gcc 14 + mpich on rocky 8)
 you may need to add mkmf to your path or make other adjustments to the mkmf template to run elsewhere'''

import os
from shutil  import rmtree
from pathlib import Path

import pytest
import subprocess

from fre.make import run_fremake_script

# command options
YAMLDIR = "fre/make/tests/null_example"
YAMLFILE = "null_model.yaml"
YAMLPATH = f"{YAMLDIR}/{YAMLFILE}"
PLATFORM = [ "ci.gnu" ]
CONTAINER_PLATFORM = ["hpcmini.2025"]
TARGET = ["debug"]
EXPERIMENT = "null_model_full"
VERBOSE = False

# set up some paths for the tests to build in
# the TEST_BUILD_DIR env var is used in the null model's platform.yaml
# so the model root directory path can be changed
currPath=os.getcwd()
SERIAL_TEST_PATH=f"{currPath}/fre/make/tests/compilation/serial_build"
MULTIJOB_TEST_PATH=f"{currPath}/fre/make/tests/compilation/multijob_build"
Path(SERIAL_TEST_PATH).mkdir(parents=True,exist_ok=True)
Path(MULTIJOB_TEST_PATH).mkdir(parents=True,exist_ok=True)

# check if we have required programs installed on our current system
retstat, version = subprocess.getstatusoutput('gcc --version')
has_gcc = retstat == 0
retstat, version = subprocess.getstatusoutput('mpicc --version')
has_mpi = retstat == 0
retstat, version = subprocess.getstatusoutput('nc-config --version')
has_ncdf = retstat == 0
## TODO this works, but hardcoded mkmf template path makes it fail
can_compile = has_gcc and has_mpi and has_ncdf

retstat, version = subprocess.getstatusoutput('podman --version')
has_podman = retstat == 0
retstat, version = subprocess.getstatusoutput('apptainer --version')
has_apptainer = retstat == 0
can_container = has_apptainer and has_podman

# test building the null model using gnu compilers
@pytest.mark.skipif(not can_compile, reason="missing GNU compiler, mpi, or netcdf")
def test_run_fremake_serial_compile():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    os.environ["TEST_BUILD_DIR"] = SERIAL_TEST_PATH
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET, False, 1, False, True, VERBOSE)
    assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/{EXPERIMENT}.x").exists()

# same test with a parallel build
@pytest.mark.skipif(not can_compile, reason="missing GNU compiler, mpi, or netcdf")
def test_run_fremake_multijob_compile():
    ''' test run-fremake parallel compile with gnu'''
    os.environ["TEST_BUILD_DIR"] = MULTIJOB_TEST_PATH
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET, True, 4, False, True, VERBOSE)
    assert Path(f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/{EXPERIMENT}.x").exists()

# containerized build
@pytest.mark.skipif(not can_container, reason="missing podman")
def test_run_fremake_container_build():
    ''' checks image creation for the container build'''
    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLATFORM, TARGET, False, 1, True, True, VERBOSE)
    assert Path("null_model_full-debug.sif").exists()
