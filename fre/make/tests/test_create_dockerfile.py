''' test "fre make create-dockerfile" calls '''

import os
from shutil  import rmtree
from pathlib import Path

from click.testing import CliRunner

import pytest

from fre import fre
from fre.make import create_docker_script 

runner=CliRunner()

# command options
YAMLDIR = "fre/make/tests/null_example"
YAMLFILE = "null_model.yaml"
YAMLPATH = f"{YAMLDIR}/{YAMLFILE}"
PLATFORM = ["hpcme.2023"]
TARGET = ["debug"]
BADOPT = ["foo"]
EXPERIMENT = "null_model_full"
VERBOSE = False

# possible targets
targets = ["debug", "prod", "repro", "debug-openmp", "prod-openmp", "repro-openmp"]

# set up some paths for the tests
TEST_PATH="fre/make/tests/test_create_dockerfile"
Path(TEST_PATH).mkdir(parents=True,exist_ok=True)

## def dockerfile_create(yamlfile,platform,target,execute):

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
    ''' test -fremake with a invalid platform option'''
    create_docker_script.dockerfile_create(YAMLPATH, BADOPT, TARGET, False)

@pytest.mark.xfail()
def test_bad_target_option():
    ''' test create-dockerfile with a invalid target option'''
    create_docker_script.dockerfile_create(YAMLPATH, PLATFORM, BADOPT, False)

@pytest.mark.xfail()
def test_bad_yamlpath_option():
    ''' test create-dockerfile with a invalid target option'''
    create_docker_script.dockerfile_create(BADOPT[0], PLATFORM, TARGET, False)


# tests container build script/makefile/dockerfile creation
def test_create_dockerfile():
    '''run create-dockerfile with options for containerized build'''
    create_docker_script.dockerfile_create(YAMLPATH, PLATFORM, TARGET, False)

def test_create_dockerfile_build_script_creation():
    ''' checks container build script creation from previous test '''
    assert Path("createContainer.sh").exists()

def test_create_dockerfile_dockerfile_creation_container():
    ''' checks dockerfile creation from previous test '''
    assert Path("Dockerfile").exists()

#def test_create_dockerfile_checkout_script_creation_container():
    #''' checks checkout script creation from previous test '''
    #assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/checkout.sh").exists()

#def test_create_dockerfile_makefile_creation_container():
    #''' checks makefile creation from previous test '''
    #assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/Makefile").exists()

#def test_run_dockerfile_create_script_creation_container():
    #''' checks (internal) container run script creation from previous test '''
    #assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/execrunscript.sh").exists()

# tests for builds with multiple targets

#def test_run_fremake_bad_target():
    #''' checks invalid target returns an error '''
    #os.environ["TEST_BUILD_DIR"] = MULTITARGET_TEST_PATH
    #result = runner.invoke(fre.fre, args=["make", "create-dockerfile", "-y", YAMLPATH, "-p", PLATFORM[0], "-t", "prod-repro"])
    #assert result.exit_code == 1

#def test_run_fremake_multiple_targets():
    #''' passes all valid targets for a build '''
    #result = runner.invoke(fre.fre, args=["make", "create-dockerfile", "-y", YAMLPATH, "-p", PLATFORM[0], "-t",  \
                                          #"debug", "-t", "prod", "-t", "repro", "-t", "debug-openmp", "-t",\
                                          #"prod-openmp", "-t", "repro-openmp"])
    #assert result.exit_code == 0

#def test_run_fremake_compile_script_creation_multitarget():
#    ''' check compile scripts for all targets exist from previous test'''
    #for t in targets:
        #assert Path(f"{MULTITARGET_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{t}/exec/compile.sh").exists()

#def test_run_fremake_checkout_script_creation_multitarget():
    #''' check for checkout script creation for mulit-target build'''
    #''' check checkout script exists from previous test'''
    #assert Path(f"{MULTITARGET_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

#def test_run_fremake_makefile_creation_multitarget():
    #''' check for makefile creation from previous test '''
    #for t in targets:
        #assert Path(f"{MULTITARGET_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{t}/exec/Makefile").exists()
