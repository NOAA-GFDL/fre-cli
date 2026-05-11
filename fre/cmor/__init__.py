''' compatibility shims for disabled fre.cmor entry points '''

FREMOR_URL = 'https://github.com/NOAA-GFDL/fremor'
CMOR_DISABLED_MESSAGE = f'fre.cmor has been disabled in fre-cli; use fremor instead: {FREMOR_URL}'


def disabled_cmor_subtool(*args, **kwargs):
    ''' raise the standard disabled fre.cmor error '''
    del args, kwargs
    raise NotImplementedError(CMOR_DISABLED_MESSAGE)


cmor_run_subtool = disabled_cmor_subtool
cmor_find_subtool = disabled_cmor_subtool
cmor_yaml_subtool = disabled_cmor_subtool
cmor_config_subtool = disabled_cmor_subtool
