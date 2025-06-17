import yaml
import os
import re

# Removes enclosing braces or parentheses and optionally leading dollar sign from a string
# \param inString A string from which characters will be removed
# \param bound A set of characters to be removed from the beginning and end of the string
# \param leadingDollar (optional) If True, removed leading dollar sign


def removeEnclosing(inString, bound='()', leadingDollar=True):
    if leadingDollar:
        inString = inString.lstrip('$')
    return inString.lstrip(bound[0]).rstrip(bound[1])

# Retrieves an environmental variable based on a string of the form $(VAR)
# \param inString A string that specifies the variable to be retrieved


def getEnvSub(inString):
    return os.getenv(removeEnclosing(inString.group(), bound='{}'))

# Replaces all instances of Linux environment variables (${VAR}) in a string using getEnvSub
# \param string A string to have the variables replaced


def envReplace(string):
    return re.sub("\\$\\{\\w+\\}", getEnvSub, string)

# Reads stores and replaces the fre variables set in the model YAML


class frevars():
    # Grabs the FRE variables from the model yaml
    # \param self The frevars object
    # \param y The model yaml file name
    def __init__(self, y):
        self.modelyaml = y  # no need to load - already in dictionary format

# Substitutes fre variables with the format $(variable) into the input string
# \string The string that contains the variables
# \returns String with the fre variables filled in
    def freVarReplace(self, string):
        # Retrieves a value from the modelyaml based on a key of the form $(VAR)
        # \param inString A string that specifies the value to be retrieved
        def getVarYamlSub(inString):
            return self.modelyaml[removeEnclosing(inString.group())]
        return re.sub("\\$\\(\\w+\\)", getVarYamlSub, string)

# Wrapper that relaces environment ${} and FRE $() variables
# \param self the FRE yaml varaibles (FRE properties)
# \param string The YAML string that is having its variables replaced
# \returns string with the environment and FRE variables replaced
    def freVarSub(self, string):
        tmpString = envReplace(string)
        returnString = self.freVarReplace(tmpString)
        return returnString

# Wrapper that takes in a string (yaml) and fills in the FRE and Environment variables
# \param y Path to yaml file whose variables need to be filled in
    def fillInYamlWithVars(self, y):
        with open(y, 'r') as file:
            yamlString = read(file)
        return self.freVarSub(yamlString)
