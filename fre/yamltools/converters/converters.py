from pathlib import Path
import yaml

from bs4 import BeautifulSoup 

from xml import XML


class CompileConverter(XML):
    
    def __init__(self, xmlfile: str|Path, experiment_name: str = None):

        super().__init__(xmlfile)

        self.experiment_name = experiment_name
        self.experiments = self.set_experiments(experiment_name)
        self.yamldicts = {}

        
    def convert(self, experiment_name: str = None):
        
        for experiment_name, experiment in self.experiments.items():                    
            compile_yaml = {"compile": {
                "experiment": experiment_name,
                "container_addlibs": "",
                "baremetal_linkerflags": "",
                "src": self.get_src_list(experiment)}
            }
            self.yamldicts[experiment_name] = compile_yaml        

            self.write_yaml(compile_yaml, "compile_"+experiment_name +".yaml")
            
        
    def write_yaml(self, yamldict: dict, yamlfile: str|Path):    

        with open(yamlfile, "w") as openedfile:
            yaml.dump(yamldict, openedfile, sort_keys=False)


    def set_experiments(self, experiment_name: str = None):

        prettyname = lambda name: name.replace("$(", "").replace(")", "")
        
        experiments = self.find_all("experiment", search_name=experiment_name)

        if experiments:
            return {
                prettyname(self.get_key("name", experiment)): experiment for experiment in experiments
            }

        raise RuntimeError("Cannot find experiments")

            
    def get_src_list(self, experiment, component_name: str = None):

        components = self.find_all("component", experiment, component_name)
        
        src_list = []
        for component in components:

            component_yaml = {
                "component": self.get_key("name", component),
                "branch": self.get_tag("codeBase", component, "version"),
                "repo": self.get_tag("source", component, "root") + "/" + self.get_tag("codeBase", component),
                "paths": self.make_list(self.get_key("paths", component)),
                "requires": self.make_list(self.get_key("requires", component)),
                "otherFlags": self.make_list(self.get_key("includeDir", component)),
                "cppdefs": self.get_tag("cppDefs", component),
                "makeOverrides": self.get_tag("makeOverrides", component),
                "doF90Cpp": self.get_tag("compile", component, "doF90Cpp"),
                "additionalInstructions": self.make_list(self.get_tag("csh", component), "\n")
            }
            
            src_list.append(
                {key: value for key, value in component_yaml.items() if value is not None}
            )
            
        return src_list
