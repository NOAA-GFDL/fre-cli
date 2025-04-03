import os
import json
from pathlib import Path
import yaml
from jsonschema import validate, ValidationError, SchemaError
from . import platformfre

def parseCompile(fname,v):
    """
    Brief: Open the yaml file and parse as fremakeYaml
    Param:
        - fname yaml dictionary to parse
        - v the FRE yaml variables
    """
    # Convert yaml dictionary to string and substitute ${ -- }
    y = v.freVarSub(str(fname))

    return y

class compileYaml():
    """
    Brief: This will read the compile yaml for FRE and then fill in any of the missing non-required variables
    """
    def __init__(self,compileinfo):
        """
        Brief: Read get the compile yaml and fill in the missing pieces
        Param:
            - self the compile Yaml object
            - compileinfo dictionary with compile information from the combined yaml
        """
        # compile information from the combined yaml
        self.yaml = compileinfo
        # Check if self.yaml is None
        if self.yaml is None:
            raise ValueError("The provided compileinfo is None. It must be a valid dictionary.")
        ## Check for required experiment name
        try:
            self.yaml["experiment"]
        except KeyError:
            raise KeyError("You must set an experiment name to compile \n")
        ## Check for optional libraries and packages for linking in container
        try:
            self.yaml["container_addlibs"]
        except:
            self.yaml["container_addlibs"]=""
        ## Check for optional libraries and packages for linking on bare-metal system
        try:
            self.yaml["baremetal_linkerflags"]
        except:
            self.yaml["baremetal_linkerflags"]=""
        ## Check for required src
        try:
            self.yaml["src"]
        except:
            print("You must set a src to specify the sources in modelRoot/"+self.yaml["experiment"]+"\n")
            raise
        ## Loop through the src array
        for c in self.yaml['src']:
        ## Check for required componenet name
            try:
                c['component']
            except:
                print("You must set the 'componet' name for each src component")
                raise
            ## Check for required repo url
            try:
                c['repo']
            except:
                print("'repo' is missing from the component "+c['component']+" in "+self.yaml["experiment"]+"\n")
                raise
            # Check for optional branch. Otherwise set it to blank
            try:
                c['branch']
            except:
                c['branch']=""
            # Check for optional cppdefs. Otherwise set it to blank
            try:
                c['cppdefs']
            except:
                c['cppdefs']=""
            # Check for optional doF90Cpp. Otherwise set it to False
            try:
                c['doF90Cpp']
            except:
                c['doF90Cpp']=False
            # Check for optional additional instructions. Otherwise set it to blank
            try:
                c['additionalInstructions']
            except:
                c['additionalInstructions']=""
            # Check for optional paths. Otherwise set it to blank
            try:
                c['paths']
            except:
                c['paths']=[c['component']]
            # Check for optional requires. Otherwise set it to blank
            try:
                c['requires']
            except:
                c['requires']=[]
            # Check for optional overrides. Otherwise set it to blank
            try:
                c['makeOverrides']
            except:
                c['makeOverrides']=""
            # Check for optional flags. Otherwise set it to blank.
            try:
                c["otherFlags"]
            except:
                c["otherFlags"]=""

    def getCompileYaml(self):
        """
        Brief: Returns the compile yaml
        """
        try:
            self.yaml
        except:
            print ("You must initialize the compile YAML object before you try to get the yaml \n")
            raise
        return self.yaml

class freyaml():
    """
    Brief: This will take the combined yaml file, parse information, and fill in missing variables 
           to make the full freyaml that can be used and checked
    Note:
        - platformYaml: platforms.yaml
        - compileYaml: compile.yaml
    """
    def __init__(self,combinedyaml,v):
        """
        Param:
            - self The freyaml object
            - combinedyaml The name of the combined yaml file
            - v FRE yaml variables
        """
        self.combinedfile = combinedyaml  #yaml dictionary
        self.freyaml = parseCompile(self.combinedfile,v)

        # convert edited string back to dictionary
        self.freyaml = eval(self.freyaml)

        #get compile info
        self.compiledict = self.freyaml.get("compile")
        self.compile = compileYaml(self.compiledict)
        self.compileyaml = self.compile.getCompileYaml()

        #self.freyaml.update(self.compileyaml)

        #get platform info
        self.platformsdict = self.freyaml.get("platforms")
        self.platforms = platformfre.platforms(self.platformsdict)
        self.platformsyaml = self.platforms.getPlatformsYaml()

        #self.freyaml.update(self.platformsyaml)

        ## VALIDATION OF COMBINED YAML FOR COMPILATION
        fremake_package_dir = Path(__file__).resolve().parents[2]
        schema_path = os.path.join(fremake_package_dir, 'gfdl_msd_schemas', 'FRE', 'fre_make.json')
        with open(schema_path, 'r') as f:
            s = f.read()
        schema = json.loads(s)

        validate(instance=self.freyaml,schema=schema)
        print("\nCOMBINED YAML VALID")

    def getCompileYaml(self):
        """
        Brief: Returns the compile yaml
        """
        return self.compileyaml

    def getPlatformsYaml(self):
        """
        Brief: Returns the compile yaml
        """
        return self.platformsyaml
