"""
module init file for fre. sets the version attribute, and sets up a fre_logger
"""

import logging
# all non-release states of fre-cli (e.g. fre/test, local installs) are versioned as 'develop',
# consistent with the conda package version (fre-cli==develop).
# publish_conda.yml replaces this with the tag when building a release package.
DEV_VERSION = "develop"
version = DEV_VERSION
__version__ = version

def is_dev_version(ver: str = version) -> bool:
    """
    Check if a fre-cli version string represents a development (non-release) version.

    :param ver: is a fre-cli version string. Defaults to the installed version.
    :type ver: str
    :return: True if the version is 'develop'
    :rtype: bool
    """
    return str(ver) == DEV_VERSION

fre_logger = logging.getLogger(__name__)

FORMAT = "[%(levelname)5s:%(filename)24s:%(funcName)24s] %(message)s"
logging.basicConfig(level = logging.WARNING,
                    format = FORMAT,
                    filename = None,
                    encoding = 'utf-8' )
