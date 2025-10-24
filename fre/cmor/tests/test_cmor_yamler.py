import pytest
from fre.cmor.cmor_yamler import cmor_yaml_subtool

def test_modelyaml_dne_raise_filenotfound():
    with pytest.raises(FileNotFoundError):
        cmor_yaml_subtool( yamlfile = "MODEL YAML DOESNT EXIST",
                           exp_name = "FOO",
                           platform = "BAR",
                           target = "BAZ",
                           dry_run_mode = True )
