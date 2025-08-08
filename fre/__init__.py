"""
module init file for fre. sets the version attribute, and sets up a fre_logger
"""

import importlib.metadata
import logging

fre_logger=logging.getLogger(__name__)
FORMAT = "%(levelname)s:%(filename)s:%(funcName)s %(message)s"
logging.basicConfig(level = logging.WARNING, format=FORMAT,
                    filename = None, encoding = 'utf-8' )

# versioning, turn xxxx.y into xxxx.0y
version_unexpanded = importlib.metadata.version('fre-cli')
version_unexpanded_split = version_unexpanded.split('.')
if len(version_unexpanded_split[1]) == 1:
    version_minor = "0" + version_unexpanded_split[1]
else:
    version_minor = version_unexpanded_split[1]
# if the patch version is present, then use it. otherwise, omit
try:
    len(version_unexpanded_split[2])
    if len(version_unexpanded_split[2]) == 1:
        version_patch = "0" + version_unexpanded_split[2]
    else:
        version_patch = version_unexpanded_split[2]
    version = version_unexpanded_split[0] + '.' + version_minor + '.' + version_patch
except IndexError:
    version = version_unexpanded_split[0] + '.' + version_minor

__version__=version
