import yaml
import json
from jsonschema import validate, ValidationError, SchemaError
import platformfre
import os

## Open the yaml file and parse as fremakeYaml
## \param fname the name of the yaml file to parse
## \param v the FRE yaml varaibles (FRE properties)
def parseCompile(fname,v):
## Open the yaml file and parse as fremakeYaml
     with open(fname, 'r') as file:
          # Substitute the variables and read the updated yaml string
          y = yaml.safe_load(v.freVarSub(file.read()))
     return y 
## \brief Checks the yaml for variables.  Required variables will dump and error.  Non-required variables will 
## set a default value for the variable
## \param var A variable in the yaml
## \param val a default value for var
## \param req if true, the variable is required in the yaml and an exception will be raised
## \param err An error message to print if the variable is required and doesn't exist
def yamlVarCheck(var,val="",req=False,err="error"):
     try:
          var
     except:
          if req:
               print (err)
               raise
          else:
               var = val
## This will read the compile yaml for FRE and then fill in any of the missing non-required variables
class compileYaml():
## Read get the compile yaml and fill in the missing pieces
## \param self the compile Yaml object
## \yamlFile The path to the compile yaml file
## \v The FRE variables set in the model yaml
 def __init__(self,yamlFile,v):
     self.file = yamlFile
     self.yaml = parseCompile(self.file,v)
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
#     ## Set up the srcDir
#     self.src = modelRoot + "/" + self.yaml["experiment"] + "/src"
     ## Check for required src
     try:
          self.yaml["src"]
     except:
          print("You must set a src to specify the sources in "+self.yaml["experiment"]+"\n")
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

## Returns the compile yaml
 def getCompileYaml(self):
     try:
          self.yaml
     except:
          print ("You must initialize the compile YAML object before you try to get the yaml \n")
          raise
     return self.yaml

#########################################################################################################################
## \description This will take the models yaml file which has a list of the sub yaml files and combine them into the 
## full freyaml that can be used and checked
# platformYaml: platforms.yaml
# layoutYaml:
# compileYaml: compile.yaml
# experiments:

class freyaml():
## \param self The freyaml object
## \param modelFileName The name of the model yaml file
## \param v the FRE yaml varaibles object (FRE properties)
 def __init__(self,modelFileName,v):
     self.freyaml = {}
     self.modelfile = modelFileName
     with open(self.modelfile, 'r') as file:
          self.modelyaml = yaml.safe_load(v.freVarSub(file.read()))
     self.freyaml.update(self.modelyaml)
     self.compilefile = self.modelyaml["compileYaml"]
     self.compile = compileYaml(self.compilefile,v)
     self.compileyaml = self.compile.getCompileYaml()
     self.freyaml.update(self.compileyaml)
     self.platformsfile = self.modelyaml["platformYaml"]
     self.platforms = platformfre.platforms(self.platformsfile,v)
     self.platformsyaml = self.platforms.getPlatformsYaml()
     self.freyaml.update(self.platformsyaml)
## Validate the YAML
     fremake_package_dir = os.path.dirname(os.path.abspath(__file__))
     schema_path = os.path.join(fremake_package_dir, 'schema.json')
     with open(schema_path, 'r') as f:
         s = f.read()
     schema = json.loads(s)
     validate(instance=self.freyaml, schema=schema)
## \return platform yaml dictionary
 def getPlatformsYaml(self):
     return self.platformsyaml
## \return compile yaml dictionary
 def getCompileYaml(self):
     return self.compileyaml
