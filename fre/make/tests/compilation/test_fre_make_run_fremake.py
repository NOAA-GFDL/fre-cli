''' test "fre make run-fremake" calls '''

import os
from pathlib import Path

import pytest

from fre.make import runFremake


# command options
YAMLFILE = "fre/make/tests/null_example/null_model.yaml"
PLATFORM = [ "ci.gnu" ]
CONTAINER_PLATFORM = ["hpcme.2023"]
TARGET = ["debug"]
EXPERIMENT = "null_model_full"

# get HOME dir to check output
HOME_DIR = os.environ["HOME"]

@pytest.mark.skip(reason='failing: fix in development, see PR 275')
def test_fre_make_run_fremake_null_model_serial_compile():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    runFremake.fremake_run(YAMLFILE, PLATFORM, TARGET, False, 1, False, False)
    assert Path(f"{HOME_DIR}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/{EXPERIMENT}.x").exists()

