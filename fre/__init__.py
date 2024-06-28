# not sure if these are still needed to follow Pythonic conventions, the code seems to work even when these are removed/commented out
from .check import *
from .list import *
from .make import *
from .pp import *
from .run import *
from .catalog import *
from .yamltools import *
from .app import *
from .cmor import *
from .lazy_group import LazyGroup

from . import _version
__version__ = _version.get_versions()['version']
