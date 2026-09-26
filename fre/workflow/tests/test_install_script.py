''' fre workflow checkout tests '''
import stat
import re
import os
from pathlib import Path
import pytest
from fre.workflow import install_script

TEST_CONFIGS = "fre/workflow/tests/AM5_example/"
EXPERIMENT = "c96L65_am5f7b12r1_amip_TESTING"

@pytest.fixture(autouse=True, name="fake_home")
def fake_home_fixture(tmp_path, monkeypatch):
    """
    Set the tmp_path as HOME for the cylc-src directory
    to be created in.
    """
    ## Mock HOME for cylc-src and cylc-run
    fake_home = Path(tmp_path)
    monkeypatch.setenv("HOME", str(fake_home))

    return fake_home

@pytest.fixture(autouse=True, name="fake_exp_src_dir")
def fake_exp_src_dir_fixture(fake_home):
    """
    """
    src_dir = f"{fake_home}/cylc-src/{EXPERIMENT}"
    Path(src_dir).mkdir(parents=True)

    # create workflow definition
    definition_content = "flow.cylc content"
    Path(f"{src_dir}/flow.cylc").write_text(definition_content)

    yaml_content = "name: ah"
    Path(f"{src_dir}/config.yaml").write_text(yaml_content)

    #####should I dump the yaml instead???

    assert Path(f"{src_dir}/flow.cylc").exists()
    assert Path(f"{src_dir}/flow.cylc").is_file()
    assert Path(f"{src_dir}/config.yaml").exists()
    assert Path(f"{src_dir}/config.yaml").is_file()

##mock cylc-src, mock exp in cylc-src, mock flow.cylc
##test install
def test_install_script(fake_home, caplog, capfd):
    """
    """
    try:
       install_script.workflow_install(experiment = EXPERIMENT)
    except:
        assert False

#    print(caplog.text)
#    print(type(capfd.readouterr().err))
#    ah
    assert all([Path(f"{fake_home}/cylc-run/{EXPERIMENT}").exists(),
                Path(f"{fake_home}/cylc-run/{EXPERIMENT}").is_dir(),
                Path(f"{fake_home}/cylc-run/{EXPERIMENT}/flow.cylc").exists(),
                Path(f"{fake_home}/cylc-run/{EXPERIMENT}/flow.cylc").is_file(),
                f"INSTALLED {EXPERIMENT} from {fake_home}/cylc-src/{EXPERIMENT}" in capfd.readouterr().out,
                #"INFO - Passing resolved YAML information to install." in capfd.readouterr().err,
                f"NOTE: About to install workflow into ~/cylc-run/{EXPERIMENT}" in caplog.text])

    with open(Path(f"{fake_home}/cylc-run/{EXPERIMENT}/flow.cylc"), "r") as f:
        expected_content = "flow.cylc content"
        wdf = f.read()
        if expected_content in wdf:
            assert True
        else:
            assert False
