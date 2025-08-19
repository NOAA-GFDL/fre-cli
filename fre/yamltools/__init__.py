"""
other bits in fre.yamltools use this with a 'from . import *'. This way, the 
yaml module understands what to do with the '!join' references in our yaml files
when they appear.
"""
import yaml
from .constructors import _join_constructor
yaml.add_constructor('!join', _join_constructor)
