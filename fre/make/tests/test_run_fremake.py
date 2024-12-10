''' test "fre make run-fremake" calls '''
''' these tests assume your os is the ci image (gcc 14 + mpich on rocky 8)'''

import os
from shutil  import rmtree
from pathlib import Path

import pytest

from fre.make import run_fremake_script


# command options
YAMLDIR = "fre/make/tests/null_example"
YAMLFILE = "null_model.yaml"
YAMLPATH = f"{YAMLDIR}/{YAMLFILE}"
PLATFORM = [ "ci.gnu" ]
CONTAINER_PLATFORM = ["hpcme.2023"]
TARGET = ["debug"]
BADOPT = ["foo"]
EXPERIMENT = "null_model_full"
VERBOSE = False 

# set up some paths for the tests
SERIAL_TEST_PATH="fre/make/tests/test_run_fremake_serial"
MULTIJOB_TEST_PATH="fre/make/tests/test_run_fremake_multijob"

Path(SERIAL_TEST_PATH).mkdir(parents=True,exist_ok=True)
Path(MULTIJOB_TEST_PATH).mkdir(parents=True,exist_ok=True)

# get HOME dir to check output

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
    run_fremake_script.fremake_run(YAMLPATH, BADOPT, TARGET, False, 1, False, False, VERBOSE)

@pytest.mark.xfail()
def test_bad_target_option():
    ''' test run-fremake with a invalid target option'''
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, BADOPT, False, 1, False, False, VERBOSE)

@pytest.mark.xfail()
def test_bad_yamlpath_option():
    ''' test run-fremake with a invalid target option'''
    run_fremake_script.fremake_run(BADOPT[0], PLATFORM, TARGET, False, 1, False, False, VERBOSE)


# test script/makefile creation without executing (serial compile)
def test_fre_make_run_fremake_compile_script_serial():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    os.environ["TEST_BUILD_DIR"] = SERIAL_TEST_PATH 
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET, False, 1, False, False, VERBOSE)
    assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/compile.sh").exists()

def test_fre_make_run_fremake_checkout_script_creation_serial():
    ''' check for checkout script creation from previous test '''
    assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_fre_make_run_fremake_makefile_creation_serial():
    ''' check for makefile creation from previous test '''
    assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/Makefile").exists()

# test script/makefile creation without executing (multijob, with non-parallel-checkout)
def test_fre_make_run_fremake_multijob_compile_script():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    os.environ["TEST_BUILD_DIR"] = MULTIJOB_TEST_PATH 
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET, True, 4, True, False, VERBOSE)
    assert Path(f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/compile.sh").exists()

def test_fre_make_run_fremake_checkout_script_creation_multijob():
    ''' check for checkout script creation from previous test '''
    assert Path(f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_fre_make_run_fremake_makefile_creation_multijob():
    ''' check for makefile creation from previous test '''
    assert Path(f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/Makefile").exists()

# dockerfile tests

#def test_fre_make_run_fremake_dockerfile_creation():
#    ''' checks dockerfile creation for the container build'''
#    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLATFORM, TARGET, False, 1, False, False, VERBOSE)

