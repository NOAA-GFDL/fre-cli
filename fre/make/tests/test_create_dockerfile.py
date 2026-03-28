''' test "fre make dockerfile" calls '''

import os
from shutil  import rmtree
from pathlib import Path

from click.testing import CliRunner

import pytest

from fre.make import create_docker_script

runner=CliRunner()

# Compute repo root
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

# command options
YAMLDIR = os.path.join(repo_root, "fre/make/tests/null_example")
YAMLFILE = "null_model.yaml"
YAMLPATH = os.path.join(YAMLDIR, YAMLFILE)
PLATFORM = ["hpcme.2023"]
TARGET = ["debug"]
BADOPT = ["foo"]
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


@pytest.fixture(scope="session")
def session_tmp(tmp_path_factory):
    return tmp_path_factory.mktemp("fre_make_test")

def test_no_op_platform(monkeypatch, session_tmp):
    """
    Test create-dockerfile will do nothing if non-container platform is given
    """
    monkeypatch.chdir(session_tmp)
    if Path("tmp").exists():
        rmtree("tmp") # clear out any past runs
    create_docker_script.dockerfile_create(YAMLPATH, ["ci.gnu"], TARGET,
    	execute=False, no_format_transfer=False)
    assert not Path("tmp").exists()

# tests container build script/makefile/dockerfile creation
def test_create_dockerfile(monkeypatch, session_tmp):
    """
    Run create-dockerfile with options for containerized build
    """
    monkeypatch.chdir(session_tmp)
    create_docker_script.dockerfile_create(YAMLPATH, PLATFORM, TARGET,
    	execute=False, no_format_transfer=False)

def test_container_dir_creation(monkeypatch, session_tmp):
    """
    Check directories are created
    """
    monkeypatch.chdir(session_tmp)
    assert Path(f"./tmp/{PLATFORM[0]}").exists()

def test_container_build_script_creation(monkeypatch, session_tmp):
    """
    Checks container build script creation from previous test
    """
    monkeypatch.chdir(session_tmp)
    assert Path("createContainer.sh").exists()

def test_runscript_creation(monkeypatch, session_tmp):
    """ 
    Checks (internal) container run script creation from previous test
    """
    monkeypatch.chdir(session_tmp)
    assert Path(f"tmp/{PLATFORM[0]}/execrunscript.sh").exists()

def test_dockerfile_creation(monkeypatch, session_tmp):
    """
    Checks dockerfile creation from previous test
    """
    monkeypatch.chdir(session_tmp)
    assert Path("Dockerfile").exists()

def test_dockerfile_contents(monkeypatch, session_tmp):
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

def test_build_script_contents(monkeypatch, session_tmp):
    """
    Checks container build script contents from previous test. 
    Specifically - testing the volume mount is added correctly. 
    """
    monkeypatch.chdir(session_tmp)
    # Open container build script
    with open('createContainer.sh', 'r') as f:
        lines = f.readlines()

    expected_volume_mount = "podman build --volume /gpfs/f5:/gpfs/f5 -f Dockerfile -t null_model_full:debug"

    # strip off '\n'
    container_build_script = []
    for line in lines:
        container_build_script.append(line.rstrip("\n"))

    assert expected_volume_mount in container_build_script
