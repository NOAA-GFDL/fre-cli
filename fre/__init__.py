import importlib.metadata

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
log_level= 999


#import logging
## base fre_logger set here, configured within fre
#fre_logger = logging.getLogger(__name__)
##FORMAT = "%(levelname)s:%(filename)s:%(funcName)s %(message)s"
##MODE = 'x'
