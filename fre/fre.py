"""
Main host file for FRE-CLI program scripts
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
2023-2024
principal click group for main/fre allows for subgroup functions to 
be called via this script. I.e. 'fre' is the entry point
"""

import importlib.metadata

import logging
fre_logger = logging.getLogger(__name__)
FORMAT = "%(levelname)s:%(filename)s:%(funcName)s %(message)s"
#MODE = 'x'

import click
from .lazy_group import LazyGroup

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


@click.version_option(
    package_name = "fre-cli",
    version = version
)


# click and lazy group loading
@click.group(
    cls = LazyGroup,
    lazy_subcommands = {"pp": ".pp.frepp.pp_cli",
                       "catalog": ".catalog.frecatalog.catalog_cli",
                       "list": ".list_.frelist.list_cli",
                       "check": ".check.frecheck.check_cli",
                       "run": ".run.frerun.run_cli",
                       "yamltools": ".yamltools.freyamltools.yamltools_cli",
                       "make": ".make.fremake.make_cli",
                       "app": ".app.freapp.app_cli",
                       "cmor": ".cmor.frecmor.cmor_cli",
                       "analysis": ".analysis.freanalysis.analysis_cli"},
    help = click.style(
        "'fre' is the main CLI click group. It houses the other tool groups as lazy subcommands.",
        fg = 'cyan')
)
@click.option('-v', '--verbose', is_flag = True,
              default = False, help = "set logging verbosity higher",
              required = False)
@click.option('-l', '--log_file', default = None, required = False, type = str,
              help = 'path to log file for all fre calls. leave as None to print to screen')
def fre(verbose = False, log_file = None):
    ''' entry point function to subgroup functions '''
    log_level = None
    #file_mode = None if log_file is None else MODE
    if verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level = log_level, format = FORMAT,
                        filename = log_file, encoding = 'utf-8')

if __name__ == '__main__':
    fre()
