from pathlib import Path
import yaml

try:
    from .xml import XML
except ImportError:
    from xml import XML


class CompileConverter(XML):
    """
    Converter class to parse compile experiment XML blocks and convert to YAML dictionaries.
    """
    
    def __init__(self, xmlfile: str|Path, experiment_name: str = None):

        super().__init__(xmlfile)
        self.experiments = self.get_experiments(experiment_name)
        self.yaml_dicts = {}


    def get_experiments(self, experiment_name: str = None):
        """
        Parse the XML and save each compile experiment block 
        """

        #prettify name
        prettify = lambda name: name.strip().lower().replace("$(", "").replace(")", "")

        # if a particular experiment is not provided, get all compile experiments in xml    
        experiments = self.get_elements("experiment", self.soup, name=experiment_name)
        
        if experiments:
            return {
                prettify(self.get_attributes("name", experiment)): experiment for experiment in experiments
            }

        raise RuntimeError("Cannot find experiments")


    def convert(self):        
        """
        Convert XML content to YAML dictionary
        """
        
        for experiment_name, experiment_content in self.experiments.items():                    
            compile_yaml = {"compile": {
                "experiment": experiment_name,
                "container_addlibs": "",
                "baremetal_linkerflags": "",
                "src": self.parse_components(experiment_content)}
            }
            self.yaml_dicts[experiment_name] = compile_yaml        
            self.write_yaml(compile_yaml, "compile_"+experiment_name +".yaml")
                
            
    def parse_components(self, xml_content, component_name: str = None):
        """
        Parses component blocks to yaml dictionaries.  For example, converts 
       
        <component name="atmos_cubed_sphere" 
                   paths="GFDL_atmos_cubed_sphere/model, GFDL_atmos_cubed_sphere/driver/SHiELD/cloud_diagnosis.F90", 
                   requires="fms am5_phys">
          <source versionControl="git" root="https://github.com/NOAA-GFDL">
            <codeBase version="2024.01_am5">GFDL_atmos_cubed_sphere.git</codeBase>
          </source>
          <compile>
            <makeOverrides>USE_R4=$(USE_MIXED_MODE) ISA="-march=core-avx2 -qno-opt-dynamic-align"</makeOverrides>
            <cppDefs>$(F2003_FLAGS) -DSPMD -DCLIMATE_NUDGE</cppDefs>
          </compile>
        </component>
       
        to 
       
        {
        component: atmos_cubed_sphere
        repo: https://github.com/NOAA-GFDL/GFDL_atmos_cubed_sphere.git
        branch: 2024.01_am5
        paths: [GFDL_atmos_cubed_sphere/model, GFDL_atmos_cubed_sphere/driver/SHiELD/cloud_diagnosis.F90]
        requires: [fms, am5_phys]
        otherFlags: [$(F2003_FLAGS) -DSPMD -DCLIMATE_NUDGE]
        makeOverrides : [USE_R4=$(USE_MIXED_MODE), ISA="-march=core-avx2, -qno-opt-dynamic-align"]
        }
        """

        components = self.get_elements("component", xml_content, name=component_name)
        if components is None:
            return None
            
        parsed_components = []
        for component in components:

            codebase = self.get_elements("codeBase", component)
            source = self.get_elements("source", component)
            cppdefs = self.get_elements("cppDefs", component)
            compile_ = self.get_elements("compile", component)
            make_overrides = self.get_elements("makeOverrides", component)
            csh = self.get_elements("csh", component)

            component_yaml = {
                "component": self.get_attributes("name", component),
                "repo": f"{self.get_attributes('root', source)}/{self.get_values(codebase)}",
                "branch": self.get_attributes("version", codebase),
                "paths": self.get_attributes("paths", component, tolist=True),
                "requires": self.get_attributes("requires", component, tolist=True),
                "otherFlags": self.get_attributes("includeDir", component, tolist=True),
                "cppdefs": self.get_values(cppdefs),
                "makeOverrides": self.get_values(make_overrides),
                "doF90Cpp": self.get_attributes("doF90Cpp", compile_),
                "additionalInstructions": self.get_values(csh, tolist=True, fieldsep="\n")
            }
            
            #remove None
            component_yaml = {key: value for key, value in component_yaml.items() if value is not None}
            parsed_components.append(component_yaml)
            
        return parsed_components


    def write_yaml(self, yamldict: dict, yamlfile: str|Path):           
        """
        Write YAML dictionary to file
        """

        with open(yamlfile, "w", encoding="utf-8") as openedfile:
            yaml.dump(yamldict, openedfile, sort_keys=False)


xml = CompileConverter("compile_experiment.xml")
xml.convert()