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

# miniver (minimal versioning tool) https://github.com/jbweston/miniver
from ._version import __version__
del _version
