# Test of list_datasets_script.py by creatinga  temporary 
import yaml

def test_your_dataset_function(tmp_path):
    # Raw yaml based on combined.yaml
    yaml_content = """run:
  workflow:
    repository: ah.git
  input:
    namelist:
      files:
      - $(includeDir)/nml/am5_amip.nml
    datasets:
      common_LM4p2:
      - label: input
        target: INPUT/soil_type.nc
        chksum: ''
        timestamp: ''
        platform: $(platform)
        source: $(MODEL_GEN5_INPUTS)/common_LM4/soil_type_gsde_5minute.nc"""

    # Create the temporary file path using pytest's tmp_path
    tmp_yaml = tmp_path / "test_config.yaml"
    
    # Write the content to the temporary file
    tmp_yaml.write_text(yaml_content)

    # (Optional) Verify it loads correctly in your test
    with open(tmp_yaml, "r") as f:
        data = yaml.safe_load(f)
        
