'''
Holds any tests that compile model code or create runtime containers
baremetal tests will be skipped unless gcc/mpi/netcdf is in your path
for container tests, apptainer and singularity are required instead
tests will always run in CI testing
'''

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
CONTAINER_PLATFORM_2 = ["hpcmini.2025.Specify.Location"]
TARGET = ["debug"]
EXPERIMENT = "null_model_full"
VERBOSE = False

# set up some paths for the tests to build in
# the TEST_BUILD_DIR env var is used in the null model's platform.yaml
# so the model root directory path can be changed
currPath=os.getcwd()
SERIAL_TEST_PATH=f"{currPath}/fre/make/tests/compilation/serial_build"
MULTIJOB_TEST_PATH=f"{currPath}/fre/make/tests/compilation/multijob_build"
CONTAINER_BUILD_TEST_PATH=f"{currPath}/fre/make/tests/compilation/container"
Path(SERIAL_TEST_PATH).mkdir(parents=True,exist_ok=True)
Path(MULTIJOB_TEST_PATH).mkdir(parents=True,exist_ok=True)
Path(CONTAINER_BUILD_TEST_PATH).mkdir(parents=True,exist_ok=True)

# check if we have required programs installed on our current system
retstat, version = subprocess.getstatusoutput('gcc --version')
has_gcc = retstat == 0
retstat, version = subprocess.getstatusoutput('mpicc --version')
has_mpi = retstat == 0
retstat, version = subprocess.getstatusoutput('nc-config --version')
has_ncdf = retstat == 0
retstat, version = subprocess.getstatusoutput('mkmf -v')
has_mkmf = retstat == 0
can_compile = has_gcc and has_mpi and has_ncdf and has_mkmf

retstat, version = subprocess.getstatusoutput('podman --version')
has_podman = retstat == 0
retstat, version = subprocess.getstatusoutput('apptainer --version')
has_apptainer = retstat == 0
can_container = has_apptainer and has_podman

# test building the null model using gnu compilers
@pytest.mark.skipif(not can_compile, reason="missing GNU compiler, mpi, netcdf, or mkmf in PATH")
def test_run_fremake_serial_compile():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    os.environ["TEST_BUILD_DIR"] = SERIAL_TEST_PATH
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET,
        parallel=False, jobs=1, no_parallel_checkout=False,
        no_format_transfer=True, execute=True, verbose=VERBOSE)
    assert Path(
        f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/{EXPERIMENT}.x").exists()

# same test with a parallel build
@pytest.mark.skipif(not can_compile, reason="missing GNU compiler, mpi, netcdf, or mkmf in PATH")
def test_run_fremake_multijob_compile():
    ''' test run-fremake parallel compile with gnu'''
    os.environ["TEST_BUILD_DIR"] = MULTIJOB_TEST_PATH
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET,
        parallel=True, jobs=4, no_parallel_checkout=False,
        no_format_transfer=False, execute=True, verbose=VERBOSE)
    assert Path(
        f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/{EXPERIMENT}.x").exists()

# containerized build
@pytest.mark.skipif(not can_container, reason="missing podman/apptainer")
def test_run_fremake_container_build():
    ''' checks image creation for the container build'''
    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLATFORM, TARGET,
        parallel=False, jobs=1, no_parallel_checkout=True,
        no_format_transfer=False, execute=True, verbose=VERBOSE)
    assert Path("null_model_full-debug.sif").exists()

@pytest.mark.skipif(not can_container, reason="missing podman/apptainer")
def test_run_fremake_container_build_specified_out():
    ''' checks that the image was copied to the correct specified output location'''
    os.environ["TEST_BUILD_DIR"] = CONTAINER_BUILD_TEST_PATH
    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLATFORM_2, TARGET,
        parallel=False, jobs=1, no_parallel_checkout=True,
        no_format_transfer=False, execute=True, verbose=VERBOSE)
    assert Path(
        f"{CONTAINER_BUILD_TEST_PATH}/fremake_canopy/test/null_model_full-debug.sif").exists()

## THIS CONDITION SEEMS INSUFFICIENT ON PPAN
#@pytest.mark.skipif(not has_podman, reason="missing podman")
@pytest.mark.skipif(not can_container, reason="missing podman/apptainer")
def test_run_fremake_container_build_notransfer():
    ''' checks image creation with the .sif transfer turned off '''
    if Path("createContainer.sh").exists():
        os.remove("createContainer.sh")
    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLATFORM, TARGET,
        parallel=False, jobs=1, no_parallel_checkout=True,
        no_format_transfer=True, execute=True, verbose=VERBOSE)

def test_run_fremake_cleanup():
    ''' removes directories created by the test and checks to make sure they're gone '''
    dirstrings = ["test_run_fremake_multijob", "test_run_fremake_serial", "test_run_fremake_multitarget"]
    test_paths = [f"fre/make/tests/{el}/" for el in dirstrings]
    for tp in test_paths:
        try:
            rmtree(tp)
        except FileNotFoundError:
            print(tp + " not found for deletion. Something may have gone wrong elsewhere.")
    tp_remove = [not Path(el).exists() for el in test_paths]
    assert all(tp_remove)
    
