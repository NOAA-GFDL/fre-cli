"""
module init file for fre. sets the version attribute, and sets up a fre_logger
"""

import logging
import os
version = os.getenv("GIT_DESCRIBE_TAG", "2026.01.alpha2")
__version__ = version

fre_logger = logging.getLogger(__name__)

FORMAT = "[%(levelname)7s:%(filename)25s:%(funcName)24s] %(message)s"
logging.basicConfig(level = logging.WARNING,
                    format = FORMAT,
                    filename = None,
                    encoding = 'utf-8' )
