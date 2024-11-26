# aspirational.. like fms-yaml-tools and others specify version
#__version__ = '2024.01'


# Horrible way to turn xxxx.y into xxxx.0y
import importlib.metadata
version_unexpanded = importlib.metadata.version('fre-cli')
version_unexpanded_split = version_unexpanded.split('.')
if len(version_unexpanded_split[1]) == 1:
    version_minor = "0" + version_unexpanded_split[1]
else:
    version_minor = version_unexpanded_split[1]
version = version_unexpanded_split[0] + '.' + version_minor
__version__=version
