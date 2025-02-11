import yaml

from fre.yamltools.combine_yamls import join_constructor as jc
yaml.add_constructor("!join", jc)

file_obj=open("fre/tests/test_files/cmor.yaml",
              "r+", encoding='utf-8')


#yaml_data=yaml.safe_load(file_obj) #Loader=yaml.Loader)
yaml_data=yaml.load(file_obj, Loader=yaml.Loader)

print(yaml_data)
