import os
import json
import yaml
from jsonschema import validate, ValidationError, SchemaError
from . import platformfre

def parseCompile(fname,v):
    """
    Brief: Open the yaml file and parse as fremakeYaml
    Param:
        - fname the name of the yaml file to parse
        - v the FRE yaml variables
    """
    # Open the yaml file and parse as fremakeYaml
    with open(fname, 'r') as yamlfile:
        y = yaml.safe_load(v.freVarSub(yamlfile.read()))

    return y

##### THIS SEEMS UNUSED
## \brief Checks the yaml for variables. Required variables will dump and error. Non-required variables will
## set a default value for the variable
#def yamlVarCheck(var,val="",req=False,err="error"):
#    """
#    Brief: Checks the yaml for variables. Required variables will dump and error.
#           Non-required variables will set a default value for the variable
#    Param:
#        - var A variable in the yaml
#        - val a default value for var
#        - req if true, the variable is required in the yaml and an exception will be raised
#        - err An error message to print if the variable is required and doesn't exist
#    """
#     try:
#          var
#     except:
#          if req:
#               print (err)
#               raise
#          else:
#               var = val

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

        ## Check the yaml for required things
        ## Check for required experiment name
        try:
            self.yaml["experiment"]
        except:
            print("You must set an experiment name to compile \n")
            raise
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
        self.combinedfile = combinedyaml

        self.freyaml = parseCompile(self.combinedfile, v)

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

####TO-DO: CREATE A SCHEMA FOR THE COMBINED YAML (will apply to fre make and fre pp combiend yaml - same yaml) 
## VALIDATION OF COMBINED YAML CAN ALSO HAPPEN IN FRE YAMLTOOLS COMBINE-YAML

## Validate the YAML
#     fremake_package_dir = os.path.dirname(os.path.abspath(__file__))
#     schema_path = os.path.join(fremake_package_dir, 'schema.json')
#     with open(schema_path, 'r') as f:
#         s = f.read()
#     schema = json.loads(s)
#     validate(instance=self.combined,schema=schema)
#     print("\nCOMBINED YAML VALID")

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
