''' test "fre make run-all" calls without actual compilation '''

import os
from shutil  import rmtree
from pathlib import Path

from click.testing import CliRunner

import pytest

from fre import fre
from fre.make import run_fremake_script

runner=CliRunner()

# command options
YAMLDIR = "fre/make/tests/null_example"
YAMLFILE = "null_model.yaml"
YAMLPATH = f"{YAMLDIR}/{YAMLFILE}"
PLATFORM = [ "ci.gnu" ]
CONTAINER_PLATFORM = ["hpcme.2023"]
CONTAINER_PLAT2 = ["con.twostep"]
TARGET = ["debug"]
BADOPT = ["foo"]
EXPERIMENT = "null_model_full"
VERBOSE = False

# possible targets
targets = ["debug", "prod", "repro", "debug-openmp", "prod-openmp", "repro-openmp"]

# set up some paths for the tests
SERIAL_TEST_PATH="fre/make/tests/test_run_fremake_serial"
MULTIJOB_TEST_PATH="fre/make/tests/test_run_fremake_multijob"
MULTITARGET_TEST_PATH="fre/make/tests/test_run_fremake_multitarget"
Path(SERIAL_TEST_PATH).mkdir(parents=True,exist_ok=True)
Path(MULTIJOB_TEST_PATH).mkdir(parents=True,exist_ok=True)
Path(MULTITARGET_TEST_PATH).mkdir(parents=True,exist_ok=True)

##def fremake_run(yamlfile,platform,target,parallel,jobs,no_parallel_checkout,execute,verbose):

# yaml file checks
def test_modelyaml_exists():
    assert Path(f"{YAMLDIR}/{YAMLFILE}").exists()

def test_compileyaml_exists():
    assert Path(f"{YAMLDIR}/compile.yaml").exists()

def test_platformyaml_exists():
    assert Path(f"{YAMLDIR}/platforms.yaml").exists()

# expected failures for incorrect options
@pytest.mark.xfail()
def test_bad_platform_option():
    ''' test run-fremake with a invalid platform option'''
    run_fremake_script.fremake_run(YAMLPATH, BADOPT, TARGET,
        parallel=False, jobs=1, no_parallel_checkout=False,
	no_format_transfer=False, execute=False, verbose=VERBOSE)

@pytest.mark.xfail()
def test_bad_target_option():
    ''' test run-fremake with a invalid target option'''
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, BADOPT,
        parallel=False, jobs=1, no_parallel_checkout=False,
	no_format_transfer=False, execute=False, verbose=VERBOSE)

@pytest.mark.xfail()
def test_bad_yamlpath_option():
    ''' test run-fremake with a invalid target option'''
    run_fremake_script.fremake_run(BADOPT[0], PLATFORM, TARGET,
        parallel=False, jobs=1, no_parallel_checkout=False,
	no_format_transfer=False, execute=False, verbose=VERBOSE)

# tests script/makefile creation without executing (serial compile)
# first test runs the run-fremake command, subsequent tests check for creation of scripts
def test_run_fremake_serial():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    os.environ["TEST_BUILD_DIR"] = SERIAL_TEST_PATH
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET,
        parallel=False, jobs=1, no_parallel_checkout=False,
	no_format_transfer=False, execute=False, verbose=VERBOSE)

def test_run_fremake_compile_script_creation_serial():
    ''' check for compile script creation from previous test '''
    assert Path(
        f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/compile.sh").exists()

def test_run_fremake_checkout_script_creation_serial():
    ''' check for checkout script creation from previous test '''
    assert Path(
        f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_run_fremake_makefile_creation_serial():
    ''' check for makefile creation from previous test '''
    assert Path(
        f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/Makefile").exists()

# same tests with multijob compile and non-parallel-checkout options enabled
def test_run_fremake_multijob():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    os.environ["TEST_BUILD_DIR"] = MULTIJOB_TEST_PATH
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET,
        parallel=True, jobs=4, no_parallel_checkout=True,
	no_format_transfer=False, execute=False, verbose=VERBOSE)

def test_run_fremake_compile_script_creation_multijob():
    ''' check for compile script creation from previous test '''
    assert Path(
        f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/compile.sh").exists()

def test_run_fremake_checkout_script_creation_multijob():
    ''' check for checkout script creation from previous test '''
    assert Path(
        f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_run_fremake_makefile_creation_multijob():
    ''' check for makefile creation from previous test '''
    assert Path(
        f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/Makefile").exists()

# tests container build script/makefile/dockerfile creation
def test_run_fremake_container():
    '''run run-fremake with options for containerized build'''
    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLATFORM, TARGET,
        parallel=False, jobs=1, no_parallel_checkout=True,
	no_format_transfer=False, execute=False, verbose=VERBOSE)

def test_run_fremake_build_script_creation_container():
    ''' checks container build script creation from previous test '''
    assert Path("createContainer.sh").exists()

def test_run_fremake_dockerfile_creation_container():
    ''' checks dockerfile creation from previous test '''
    assert Path("Dockerfile").exists()

def test_run_fremake_checkout_script_creation_container():
    ''' checks checkout script creation from previous test '''
    assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/checkout.sh").exists()

def test_run_fremake_makefile_creation_container():
    ''' checks makefile creation from previous test '''
    assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/Makefile").exists()

def test_run_fremake_run_script_creation_container():
    ''' checks (internal) container run script creation from previous test '''
    assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/execrunscript.sh").exists()

# tests container 2 stage build script/makefile/dockerfile creation
def test_run_fremake_container_2stage():
    '''run run-fremake with options for containerized build'''
    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLAT2, TARGET,
        parallel=False, jobs=1, no_parallel_checkout=True,
	no_format_transfer=False, execute=False, verbose=VERBOSE)

def test_run_fremake_build_script_creation_container_2stage():
    ''' checks container build script creation from previous test '''
    assert Path("createContainer.sh").exists()

def test_run_fremake_dockerfile_creation_container_2stage():
    ''' checks dockerfile creation from previous test '''
    assert Path("Dockerfile").exists()

def test_run_fremake_checkout_script_creation_container_2stage():
    ''' checks checkout script creation from previous test '''
    cwd = os.getcwd()
    print(f"checking path: {cwd}/tmp/{CONTAINER_PLAT2[0]}/checkout.sh")
    assert Path(f"{cwd}/tmp/{CONTAINER_PLAT2[0]}/checkout.sh").exists()

def test_run_fremake_makefile_creation_container_2stage():
    ''' checks makefile creation from previous test '''
    cwd = os.getcwd()
    assert Path(f"{cwd}/tmp/{CONTAINER_PLAT2[0]}/Makefile").exists()

def test_run_fremake_run_script_creation_container_2stage():
    ''' checks (internal) container run script creation from previous test '''
    cwd = os.getcwd()
    assert Path(f"{cwd}/tmp/{CONTAINER_PLAT2[0]}/execrunscript.sh").exists()

# tests for builds with multiple targets

def test_run_fremake_bad_target():
    ''' checks invalid target returns an error '''
    os.environ["TEST_BUILD_DIR"] = MULTITARGET_TEST_PATH
    result = runner.invoke(fre.fre, args=["make", "run-all", "-y", YAMLPATH, "-p", PLATFORM[0], "-t", "prod-repro"])
    assert result.exit_code == 1

def test_run_fremake_multiple_targets():
    ''' passes all valid targets for a build '''
    result = runner.invoke(fre.fre, args=["make", "run-all", "-y", YAMLPATH, "-p", PLATFORM[0], "-t",  \
                                          "debug", "-t", "prod", "-t", "repro", "-t", "debug-openmp", "-t",\
                                          "prod-openmp", "-t", "repro-openmp"])
    assert result.exit_code == 0

def test_run_fremake_compile_script_creation_multitarget():
    ''' check compile scripts for all targets exist from previous test'''
    for t in targets:
        assert Path(
            f"{MULTITARGET_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{t}/exec/compile.sh").exists()

def test_run_fremake_checkout_script_creation_multitarget():
    ''' check for checkout script creation for mulit-target build'''
    ''' check checkout script exists from previous test'''
    assert Path(
        f"{MULTITARGET_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_run_fremake_makefile_creation_multitarget():
    ''' check for makefile creation from previous test '''
    for t in targets:
        assert Path(
            f"{MULTITARGET_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{t}/exec/Makefile").exists()
