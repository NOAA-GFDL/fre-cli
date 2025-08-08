"""
module init file for fre. sets the version attribute, and sets up a fre_logger
"""

import os
version = os.getenv("GIT_DESCRIBE_TAG", "2025.04")
__version__ = version

import logging
fre_logger = logging.getLogger(__name__)
FORMAT = "%(levelname)s:%(filename)s:%(funcName)s %(message)s"
logging.basicConfig(level = logging.WARNING, 
                    format = FORMAT,
                    filename = None, 
                    encoding = 'utf-8' )