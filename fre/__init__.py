"""
module init file for fre. sets the version attribute, and sets up a fre_logger
"""

import logging
import os
version = os.getenv("GIT_DESCRIBE_TAG", "2026.01-dev")
__version__ = version

# untagged states of fre-cli (i.e. commits to main after a tag) are versioned
# as '<last tag>-dev', e.g. 'YYYY.MM-dev' or 'YYYY.MM.alpha2-dev'
DEV_SUFFIX = "-dev"

def is_dev_version(ver: str = version) -> bool:
    """
    Check if a fre-cli version string represents an untagged development state.

    :param ver: is a fre-cli version string. Defaults to the installed version.
    :type ver: str
    :return: True if the version ends with the '-dev' suffix
    :rtype: bool
    """
    return str(ver).endswith(DEV_SUFFIX)

def base_version(ver: str = version) -> str:
    """
    Return a fre-cli version string with any '-dev' suffix removed,
    i.e. the last tag the version is based on.

    :param ver: is a fre-cli version string. Defaults to the installed version.
    :type ver: str
    :return: the version without the '-dev' suffix
    :rtype: str
    """
    ver = str(ver)
    return ver[:-len(DEV_SUFFIX)] if is_dev_version(ver) else ver

fre_logger = logging.getLogger(__name__)

FORMAT = "[%(levelname)5s:%(filename)24s:%(funcName)24s] %(message)s"
logging.basicConfig(level = logging.WARNING,
                    format = FORMAT,
                    filename = None,
                    encoding = 'utf-8' )
