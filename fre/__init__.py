"""
module init file for fre. sets the version attribute, and sets up a fre_logger
"""

import logging
import os
from typing import NoReturn
version = os.getenv("GIT_DESCRIBE_TAG", "2026.01.alpha2")
__version__ = version

fre_logger = logging.getLogger(__name__)

FORMAT = "[%(levelname)5s:%(filename)24s:%(funcName)24s] %(message)s"
logging.basicConfig(level = logging.WARNING,
                    format = FORMAT,
                    filename = None,
                    encoding = 'utf-8' )


def log_and_raise(msg, exc_type=ValueError, exc=None) -> NoReturn:
    """
    Log an error message via fre_logger and raise an exception with the same message.
    Avoids the need to duplicate error text in both fre_logger.error() and raise calls.

    Per Python logging best practices (see :pep:`282` and the
    `logging HOWTO <https://docs.python.org/3/howto/logging.html>`_):

    * ``exc_info=True`` is passed when *exc* is given so the caught exception's
      traceback is written to every configured handler (including any log file
      set up via ``fre -l``).
    * ``stack_info=True`` is always passed so the call-site stack trace appears
      in every handler, making it easy to locate the origin of the error in a
      log file.
    * ``stacklevel=2`` attributes the log record to the **caller** of
      ``log_and_raise``, not this helper itself.

    :param msg: Error message to log and include in the exception.
    :type msg: str
    :param exc_type: Exception class to raise. Defaults to ValueError.
    :type exc_type: type
    :param exc: Optional original exception to chain from (uses ``raise ... from exc``).
                When provided, ``exc_info=True`` is set so the caught exception's
                traceback is included in the log output.
    :type exc: Exception, optional
    :raises exc_type: Always raised with the given message.

    Examples::

        # raises ValueError (default) and logs the message at ERROR level
        log_and_raise("something went wrong")

        # raises a specific exception type
        log_and_raise("file not found", OSError)

        # chains from an original exception (raise ... from exc)
        except KeyError as e:
            log_and_raise("update failed", KeyError, exc=e)
    """
    if exc is not None:
        fre_logger.error(msg, exc_info=True, stack_info=True, stacklevel=2)
        raise exc_type(msg) from exc
    fre_logger.error(msg, stack_info=True, stacklevel=2)
    raise exc_type(msg)
