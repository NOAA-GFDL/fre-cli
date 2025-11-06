"""
Test fre make make_helpers
"""
from pathlib import Path
import pytest
from fre.make import make_helpers

@pytest.fixture(name="test_variables")
def test_vars_fixture():
    """
    Define variables for use in tests.
    """
    container_modelroot = "/apps"
    fre_path = Path(__file__).resolve().parents[2]
    bm_template_path = f"{fre_path}/mkmf/templates/ncrc5-intel-classic.mk"
    container_template_path = f"{container_modelroot}/mkmf/templates/hpcme-intel21.mk"

    return {
             "container_modelroot": container_modelroot,
             "fre_path": fre_path,
             "bm_template_path": bm_template_path,
             "container_template_path": container_template_path
           }

def test_mktemplate_path_bm(test_variables):
    """
    Test that the right template_path is passed if the whole path
    is given for a bare-metal build.

    The output should be the same path that was passed.
    """
    template_path = make_helpers.get_mktemplate_path(mk_template = test_variables["bm_template_path"],
                                                     model_root = None,
                                                     container_flag = False)
    assert test_variables["bm_template_path"] == template_path

def test_mktemplate_path_container(test_variables):
    """
    Test that the right template_path is passed if the whole path
    is given for a container build.

    The output should be the same path that was passed.
    """
    template_path = make_helpers.get_mktemplate_path(mk_template = test_variables["container_template_path"],
                                                     model_root = test_variables["container_modelroot"],
                                                     container_flag = True)
    assert test_variables["container_template_path"] == template_path

def test_mktemplate_name(test_variables):
    """
    Test that the right template_path is constructed if just the template
    name is given for a bare-metal build.
    """
    template_path = make_helpers.get_mktemplate_path(mk_template = "ncrc5-intel-classic.mk",
                                                     model_root = None,
                                                     container_flag = False)
    assert all(["/mkmf/templates" in template_path,
                test_variables["bm_template_path"] == template_path])

def test_mktemplate_name_container(test_variables):
    """
    Test that the right template_path is passed/constructed if just the template
    name is given for a container build.
    """
    template_path = make_helpers.get_mktemplate_path(mk_template = "hpcme-intel21.mk",
                                                     model_root = test_variables["container_modelroot"],
                                                     container_flag = True)
    assert all([test_variables["container_modelroot"] in template_path,
                test_variables["container_template_path"] == template_path])

def test_mktemplatepath_dne_with_path():
    """
    Test that a ValueError is raised if the mkTemplate path does not exist for a
    bare-metal build (given full path).
    """
    template_path = "/path/does/not/exist/dummy.mk"
    error_msg = ("Error w/ mkmf template. Created path from given filename: "
                 f"{template_path} does not exist.")
    with pytest.raises(ValueError, match = error_msg) as execinfo:
        make_helpers.get_mktemplate_path(mk_template = template_path,
                                         model_root = None,
                                         container_flag = False)
    assert execinfo.type is ValueError

def test_mktemplatepath_dne_with_name(test_variables):
    """
    Test that a ValueError is raised if the mkTemplate path does not exist for a
    bare-metal build (given name of template, not path).
    """
    template_path = "dummy.mk"
    error_msg = (f"Error w/ mkmf template. Created path from given filename: "
                 f"{test_variables['fre_path']}/mkmf/templates/{template_path} does not exist.")
    with pytest.raises(ValueError, match = error_msg) as execinfo:
        make_helpers.get_mktemplate_path(mk_template = template_path,
                                         model_root = None,
                                         container_flag = False)
    assert execinfo.type is ValueError
