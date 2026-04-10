''' stub that redirects pkg='fre-python-tools' requests to the NumpyTimeAverager '''

import logging

from .numpyTimeAverager import NumpyTimeAverager

fre_logger = logging.getLogger(__name__)


class frepytoolsTimeAverager(NumpyTimeAverager):  # pylint: disable=invalid-name
    '''
    Legacy entry-point kept for backward compatibility.
    All work is now done by NumpyTimeAverager in numpyTimeAverager.py.
    '''
