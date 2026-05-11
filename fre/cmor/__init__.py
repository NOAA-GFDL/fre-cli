''' compatibility shims for disabled fre.cmor entry points '''

FREMOR_URL = 'https://github.com/NOAA-GFDL/fremor'
CMOR_DISABLED_MESSAGE = f'fre.cmor has been disabled in fre-cli; use fremor instead: {FREMOR_URL}'


def _disabled_cmor_subtool(*args, **kwargs):
    del args, kwargs
    raise NotImplementedError(CMOR_DISABLED_MESSAGE)


cmor_run_subtool = _disabled_cmor_subtool
cmor_find_subtool = _disabled_cmor_subtool
cmor_yaml_subtool = _disabled_cmor_subtool
cmor_config_subtool = _disabled_cmor_subtool
