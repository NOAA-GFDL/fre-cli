import os
from pathlib import Path
import shutil
import yaml
import json
from jsonschema import validate, ValidationError, SchemaError
from . import platformfre

######################################
##COULD HAVE YAML_COMBINE AS A SEPARATE TOOL FOR COMPILATION AND PP YAMLS, THEN YAMLFRE.PY WOULD JUST CLEAN AND GET COMPILE/PLATFORM INFO IT NEEDS (AND DO CHECKS/VALIDAITON)
######################################
def join_constructor(loader, node):
    """
    Allows FRE properties defined
    in main yaml to be concatenated.
    """
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])

## Combine model yaml, compile yaml, and platform yaml into one yaml file
## \param self the compile Yaml object
def combineYaml(self):
     # name of combined yaml
     comb_compileyaml=f"fullcompile_{self.p}-{self.t}.yaml"

     # copy model yaml info into combined yaml
     with open(comb_compileyaml,'w+') as f1:
          f1.write(f'name: &name "{self.n}"\n')
          f1.write(f'platform: &platform "{self.p}"\n')
          f1.write(f'target: &target "{self.t}"\n\n')
          with open(self.modelfile,'r') as f2:
               f1.write("### MODEL YAML SETTINGS ###\n")
               shutil.copyfileobj(f2,f1)

     # open combined compile yaml
     with open(comb_compileyaml,'r') as f3:
          cy = yaml.load(f3,Loader=yaml.Loader)

     # Check if exp name given is actually valid experiment listed in combined yaml
     exp_list = []
     for i in cy.get("experiments"):
          exp_list.append(i.get("name"))

     if self.n not in exp_list:
         raise Exception(f"{self.n} is not in the list of experiments")

     # Extract compile yaml path for exp. provided
     # if experiment matches name in list of experiments in yaml, extract file path
     for i in cy.get("experiments"):
         if self.n == i.get("name"):
             compileyaml=i.get("compile")

     # set platform yaml
     platformyaml = cy.get("shared").get("compile").get("platformYaml")

     # copy compile and platform yaml info into combined yaml
     if compileyaml is not None:
          with open(comb_compileyaml,'a') as f1:
               for i in compileyaml:
                    with open(i,'r') as f2:
                         f1.write("\n### COMPILE INFO ###\n")
                         shutil.copyfileobj(f2,f1)

               # combine platform yaml
               if platformyaml is not None:
                    with open(platformyaml,'r') as f22:
                         f1.write("\n### PLATFORM INFO ###\n")
                         shutil.copyfileobj(f22,f1)


     # open combined compile yaml
     full_cy = parseCompile(comb_compileyaml)

     # Clean combined yaml to validate
     # If keys exists, delete:
     keys_clean=["fre_properties", "shared", "experiments"]
     for kc in keys_clean:
         if kc in full_cy.keys():
             del full_cy[kc]
     with open(comb_compileyaml,'w') as f:
         yaml.safe_dump(full_cy,f,sort_keys=False)

     return full_cy

## Open the yaml file and parse as fremakeYaml
## \param fname the name of the yaml file to parse
def parseCompile(fname):
# Open the yaml file and parse as fremakeYaml
     with open(fname, 'r') as yamlfile:
          y = yaml.load(yamlfile,Loader=yaml.Loader)

     return y 

## \brief Checks the yaml for variables.  Required variables will dump and error.  Non-required variables will 
## set a default value for the variable
## \param var A variable in the yaml
## \param val a default value for var
## \param req if true, the variable is required in the yaml and an exception will be raised
## \param err An error message to print if the variable is required and doesn't exist
#def yamlVarCheck(var,val="",req=False,err="error"):
#     try:
#          var
#     except:
#          if req:
#               print (err)
#               raise
#          else:
#               var = val

## This will read the compile yaml for FRE and then fill in any of the missing non-required variables
class compileYaml():
## Read get the compile yaml and fill in the missing pieces
## \param self the compile Yaml object
## \yamlFile The path to the compile yaml file
 def __init__(self,yamlFile):
     self.yaml = yamlFile

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
# compileYaml: compile.yaml

class freyaml():
## \param self The freyaml object
## \param modelFileName The name of the model yaml file
## \param name experiment name 
## \param platform platform used for compilation
## \param target target used in compilation
 def __init__(self,modelFileName,name,platform,target):
     #self.freyaml = {}
     self.modelfile = Path(modelFileName)
     self.n = name
     self.p = platform
     self.t = target

     yaml.add_constructor('!join', join_constructor)

     #parse
     self.combined = combineYaml(self)

## Validate the YAML
     fremake_package_dir = os.path.dirname(os.path.abspath(__file__))
     schema_path = os.path.join(fremake_package_dir, 'schema.json')
     with open(schema_path, 'r') as f:
         s = f.read()
     schema = json.loads(s)
     validate(instance=self.combined,schema=schema) 
     print("\nCOMBINED YAML VALID")

     #get compile info
     self.compiledict = self.combined.get("compile")
     self.compile = compileYaml(self.compiledict)
     self.compileyaml = self.compile.getCompileYaml()
 
     #get platform info
     self.platformsdict = self.combined.get("platforms")
     self.platforms = platformfre.platforms(self.platformsdict)
     self.platformsyaml = self.platforms.getPlatformsYaml()

## Returns the compile yaml
 def getCompileYaml(self):
     return self.compileyaml

## Returns the compile yaml
 def getPlatformsYaml(self):
     return self.platformsyaml
