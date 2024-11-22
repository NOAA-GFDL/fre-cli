"""
Test fre make create-makefile
"""
import os
import shutil
from pathlib import Path
from fre.make import createMakefile

# SET-UP
test_dir = Path("fre/make/tests")
NM_EXAMPLE = Path("null_example")
YAMLFILE = "null_model.yaml"
BM_PLATFORM = ["ncrc5.intel23"]
CONTAINER_PLATFORM = ["hpcme.2023"]
TARGET = ["debug"]
EXPERIMENT = "null_model_full"

# Create output location
out = f"{test_dir}/makefile_out"
if Path(out).exists():
    # remove
    shutil.rmtree(out)
    # create output directory
    Path(out).mkdir(parents=True,exist_ok=True)
else:
    Path(out).mkdir(parents=True,exist_ok=True)

# Set output directory as home for fre make output
#os.environ["HOME"]=str(Path(out))

def test_modelyaml_exists():
    """
    Check the model yaml exists
    """
    assert Path(f"{test_dir}/{NM_EXAMPLE}/{YAMLFILE}").exists()

def test_compileyaml_exists():
    """
    Check the compile yaml exists
    """
    assert Path(f"{test_dir}/{NM_EXAMPLE}/compile.yaml").exists()

def test_platformyaml_exists():
    """
    Check the platform yaml exists
    """
    assert Path(f"{test_dir}/{NM_EXAMPLE}/platforms.yaml").exists()

def test_bm_makefile_creation():
    """
    Check the makefile is created when a bare-metal platform is used
    """
    # Set output directory as home for fre make output
    def_home = str(os.environ["HOME"])
    os.environ["HOME"]=out#str(Path(out))

    bm_plat = BM_PLATFORM[0]
    targ = TARGET[0]
    yamlfile_path = f"{test_dir}/{NM_EXAMPLE}/{YAMLFILE}"

    createMakefile.makefile_create(yamlfile_path,BM_PLATFORM,TARGET)

    assert Path(f"{out}/fremake_canopy/test/{EXPERIMENT}/{bm_plat}-{targ}/exec/Makefile").exists()
    os.environ["HOME"]=def_home
    assert os.environ["HOME"] == def_home

def test_container_makefile_creation():
    """
    Check the makefile is created when the container platform is used
    """
    container_plat = CONTAINER_PLATFORM[0]
    yamlfile_path = f"{test_dir}/{NM_EXAMPLE}/{YAMLFILE}"
    createMakefile.makefile_create(yamlfile_path,CONTAINER_PLATFORM,TARGET)

    assert Path(f"tmp/{container_plat}/Makefile").exists()
