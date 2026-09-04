# Test of list_datasets_script.py by creatinga  temporary 
import yaml

def test_fre_list_datasets():
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
    tmp_yaml = "test_config.yaml"
    
    # Write the content to the temporary file
    tmp_yaml.write_text(yaml_content)

    # (Optional) Verify it loads correctly in your test
    with open(tmp_yaml, "r") as f:
        data = yaml.safe_load(f)

        # Call the function
    try:
         assert list_datasets_subtool(tmp_yaml)
        # Print out the returned list of dataset absolute paths
        print("\nSuccessfully retrieved datasets:")
        for path in datasets:
            print(path)
            
    except Exception as e:
        print(f"An error occurred during execution: {e}")
    #delete the temporary yaml
    if os.path.exists(tmp_yaml): os.remove(tmp_yaml)
