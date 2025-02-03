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

# container root (as set in platform yaml)
MODEL_ROOT = "/apps"

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
    create_docker_script.dockerfile_create(YAMLPATH, BADOPT, TARGET, False, False)

@pytest.mark.xfail()
def test_bad_target_option():
    ''' test create-dockerfile with a invalid target option'''
    create_docker_script.dockerfile_create(YAMLPATH, PLATFORM, BADOPT, False, False)

@pytest.mark.xfail()
def test_bad_yamlpath_option():
    ''' test create-dockerfile with a invalid yaml option'''
    create_docker_script.dockerfile_create(BADOPT[0], PLATFORM, TARGET, False, False)

def test_no_op_platform():
    '''test create-dockerfile will do nothing if non-container platform is given'''
    if Path(os.getcwd()+"/tmp").exists():
        rmtree(os.getcwd()+"/tmp") # clear out any past runs
    create_docker_script.dockerfile_create(YAMLPATH, ["ci.gnu"], TARGET, False, False)
    assert not Path(os.getcwd()+"/tmp").exists()

# tests container build script/makefile/dockerfile creation
def test_create_dockerfile():
    '''run create-dockerfile with options for containerized build'''
    if Path(f"{os.getcwd()}/Dockerfile").exists():
        Path(f"{os.getcwd()}/Dockerfile").unlink() 
        Path(f"{os.getcwd()}/createContainer.sh").unlink()
    create_docker_script.dockerfile_create(YAMLPATH, PLATFORM, TARGET, False, False)

def test_container_dir_creation():
    '''check directories are created'''
    assert Path(f"./tmp/{PLATFORM[0]}").exists()

def test_container_build_script_creation():
    ''' checks container build script creation from previous test '''
    assert Path("createContainer.sh").exists()

def test_runscript_creation():
    ''' checks (internal) container run script creation from previous test '''
    assert Path(f"tmp/{PLATFORM[0]}/execrunscript.sh").exists()

def test_dockerfile_creation():
    ''' checks dockerfile creation from previous test '''
    assert Path("Dockerfile").exists()

def test_dockerfile_contents():
    ''' checks dockerfile contents from previous test'''

    # for simplicity's sake just checks COPY commands for created files on the host 
    with open('Dockerfile', 'r') as f:
        lines = f.readlines()
    assert len(lines) > 2
    copy_lines = [ l for l in lines if l.startswith("COPY") ]

    line = copy_lines[0].strip().split()
    assert line == ["COPY", f"tmp/{PLATFORM[0]}/checkout.sh", f"{MODEL_ROOT}/{EXPERIMENT}/src/checkout.sh"]

    line = copy_lines[1].strip().split()
    assert line == ["COPY", f"tmp/{PLATFORM[0]}/Makefile", f"{MODEL_ROOT}/{EXPERIMENT}/exec/Makefile"]

    line = copy_lines[2].strip().split()
    assert line == ["COPY", f"tmp/{PLATFORM[0]}/execrunscript.sh", f"{MODEL_ROOT}/{EXPERIMENT}/exec/execrunscript.sh"]

def test_create_dockerfile_force_dockerfile(capfd):
    '''run create-dockerfile with force-dockerfile option'''
    create_docker_script.dockerfile_create(YAMLPATH, PLATFORM, TARGET, False, True)

    #Capture output
    out,err=capfd.readouterr()
    if "Re-creating Dockerfile" in out:
        assert Path("Dockerfile").exists()
        assert Path("createContainer.sh").exists()
        assert Path(f"tmp/{PLATFORM[0]}/execrunscript.sh").exists()
    else:
       assert False
