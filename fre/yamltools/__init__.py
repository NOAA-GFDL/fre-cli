# other scripts in here use this with a 'from . import *'
# this brings in the yaml module with the join_constructor
import yaml
from .constructors import join_constructor

yaml.add_constructor("!join", join_constructor)
