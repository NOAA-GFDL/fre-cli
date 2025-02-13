import click

import yaml

from fre.yamltools.combine_yamls import join_constructor as jc
yaml.add_constructor("!join", jc)








#file_obj=open("fre/tests/test_files/cmor.yaml",
#file_obj=open("fre/yamltools/tests/AM5_example/cmor_yamls/cmor.am5.yaml",
file_obj=open("fre/yamltools/tests/AM5_example/am5.yaml",
              "r+", encoding='utf-8')


#yaml_data=yaml.safe_load(file_obj) #Loader=yaml.Loader)
yaml_data=yaml.load(file_obj, Loader=yaml.Loader)

import pprint
pp = pprint.PrettyPrinter(indent=2)

pp.pprint(yaml_data)



#def main():
#    pprint_yaml()
#
#if __name__ == "__main__":
#    main()
