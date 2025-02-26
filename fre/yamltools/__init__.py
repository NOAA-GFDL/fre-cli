import yaml
from .constructors import join_constructor
yaml.add_constructor('!join', join_constructor)
