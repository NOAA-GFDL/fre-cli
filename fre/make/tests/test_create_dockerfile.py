''' test "fre make dockerfile" calls '''

import os
from shutil  import rmtree
from pathlib import Path

from click.testing import CliRunner

import pytest

from fre.make import create_docker_script

runner=CliRunner()

# command options
YAMLDIR = "fre/make/tests/null_example"
YAMLFILE = "null_model.yaml"
YAMLPATH = f"{YAMLDIR}/{YAMLFILE}"
PLATFORM = ["hpcme.2023"]
TARGET = ["debug"]
BADOPT = ["foo2"]
EXPERIMENT = "null_model_full"
VERBOSE = False

# container root (as set in platform yaml)
MODEL_ROOT = "/apps"

#def dockerfile_create(yamlfile,platform,target,execute):

# yaml file checks
def test_modelyaml_exists():
    """
    Test model yaml exists
    """
    assert Path(f"{YAMLDIR}/{YAMLFILE}").exists()

def test_compileyaml_exists():
    """
    Test compile yaml exists
    """
    assert Path(f"{YAMLDIR}/compile.yaml").exists()

def test_platformyaml_exists():
    """
    Test platform yaml exists
    """
    assert Path(f"{YAMLDIR}/platforms.yaml").exists()

# expected failures for incorrect options
@pytest.mark.xfail()
def test_bad_platform_option():
    """
    Test -fremake with a invalid platform option
    """
    create_docker_script.dockerfile_create(YAMLPATH, BADOPT, TARGET,
    	execute=False, no_format_transfer=False)

@pytest.mark.xfail()
def test_bad_target_option():
    """
    Test create-dockerfile with a invalid target option
    """
    create_docker_script.dockerfile_create(YAMLPATH, PLATFORM, BADOPT,
    	execute=False, no_format_transfer=False)

@pytest.mark.xfail()
def test_bad_yamlpath_option():
    """
    Test create-dockerfile with a invalid target option
    """
    create_docker_script.dockerfile_create(BADOPT[0], PLATFORM, TARGET,
    	execute=False, no_format_transfer=False)


def test_no_op_platform():
    """
    Test create-dockerfile will do nothing if non-container platform is given
    """
    if Path(os.getcwd()+"/tmp").exists():
        rmtree(os.getcwd()+"/tmp") # clear out any past runs
    create_docker_script.dockerfile_create(YAMLPATH, ["ci.gnu"], TARGET,
    	execute=False, no_format_transfer=False)
    assert not Path(os.getcwd()+"/tmp").exists()

# tests container build script/makefile/dockerfile creation
def test_create_dockerfile():
    """
    Run create-dockerfile with options for containerized build
    """
    create_docker_script.dockerfile_create(YAMLPATH, PLATFORM, TARGET,
    	execute=False, no_format_transfer=False)

def test_container_dir_creation():
    """
    Check directories are created
    """
    assert Path(f"./tmp/{PLATFORM[0]}").exists()

def test_container_build_script_creation():
    """
    Checks container build script creation from previous test
    """
    assert Path("createContainer.sh").exists()

def test_runscript_creation():
    """ 
    Checks (internal) container run script creation from previous test
    """
    assert Path(f"tmp/{PLATFORM[0]}/execrunscript.sh").exists()

def test_dockerfile_creation():
    """
    Checks dockerfile creation from previous test
    """
    assert Path("Dockerfile").exists()

def test_dockerfile_contents():
    """
    Checks dockerfile contents from previous test
    """

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

def test_build_script_contents():
    """
    Checks container build script contents from previous test. 
    Specifically - testing the volume mount is added correctly. 
    """
    # Open container build script
    with open('createContainer.sh', 'r') as f:
        lines = f.readlines()

    expected_volume_mount = "podman build --volume /gpfs/f5:/gpfs/f5 -f Dockerfile -t null_model_full:debug"

    # strip off '\n'
    container_build_script = []
    for line in lines:
        container_build_script.append(line.rstrip("\n"))

    assert expected_volume_mount in container_build_script
