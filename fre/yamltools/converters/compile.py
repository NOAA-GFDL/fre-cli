from pathlib import Path
import yaml

from bs4 import BeautifulSoup 

from xml import XML



class CompileXML(XML):
    
    def __init__(self, xmlfile: str|Path, yamlfile: str|Path =  None):

        super().__init__(xmlfile)

        self.yamlfile = self.xmlfile.with_suffix(".yaml") if yamlfile is None else Path(yamlfile)
        self.yaml = {}
        
            
    def convert(self):

        self.yaml["compile"]: {
            "experiment": self.get_tag(xml.soup, "experiment", "name"),
            "container_addlibs": "",
            "baremetal_linkerflags": "",
            "src": self.get_src_list()
        }

        
    def write_yaml(self):    

        with open(self.yamlfile, "w") as openedfile:
            yaml.dump(self.yaml, openedfile, sort_keys=False)


    def get_src_list(self, component_name: str = None):
        
        components = self.soup.find_all("component")
        if component_name is not None:
            components = components.find(attrs={"name": component_name})
            if components is None:
                return None
            
        src_list = []
        for component in components:

            component_yaml: ComponentSrcDict = {
                "component": self.get_key(component, "name"),
                "branch": self.get_tag(component, "codeBase", "version"),
                "repo": self.get_tag(component, "source", "root") + "/" + self.get_tag(component, "codeBase"),
                "paths": self.make_list(self.get_key(component, "paths")),
                "requires": self.make_list(self.get_key(component, "requires")),
                "otherFlags": self.make_list(self.get_key(component, "includeDir")),
                "cppdefs": self.get_tag(component, "cppDefs"),
                "makeOverrides": self.get_tag(component, "makeOverrides"),
                "doF90Cpp": self.get_tag(component, "compile", "doF90Cpp"),
                "additionalInstructions": self.make_list(self.get_tag(component, "csh", "\n"))
            }
            
            src_list.append(
                {key: value for key, value in component_yaml.items() if value is not None}
            )
            
        return src_list
            
xml = CompileXML("./compile.xml")
xml.convert()
xml.write_yaml()
