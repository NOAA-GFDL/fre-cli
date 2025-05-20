"""
Main host file for FRE-CLI program scripts
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
2023-2024
principal click group for main/fre allows for subgroup functions to
be called via this script. I.e. 'fre' is the entry point
"""



from . import version

import click

from .lazy_group import LazyGroup

import logging

# base fre_logger set here, configured within fre
fre_logger = logging.getLogger(__name__)
FORMAT = "%(levelname)s:%(filename)s:%(funcName)s %(message)s"
#MODE = 'x'

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
@click.option( '-v', '--verbose', default = 0, required = False, count = True, type = int,
               help = "increment logging verbosity. two for logging.DEBUG, one for logging.INFO" )
@click.option( '-q', '--quiet', default = False, required = False, is_flag = True, type = bool,
               help = "only output logging.ERROR messages, or worse." )
@click.option( '-l', '--log_file', default = None, required = False, type = str,
               help = 'path to log file for all fre calls. leave as None to print to screen' )
def fre(verbose = 0, quiet = False, log_file = None):
    '''
    entry point function to subgroup functions, setting global verbosity/logging formats that all
    other routines will utilize
    '''
    fre_logger.debug('setting log level')
    log_level = logging.WARN #default
    if verbose == 1:
        log_level = logging.INFO #more verbose than default
    elif verbose == 2:
        log_level = logging.DEBUG #most verbose

    if quiet:
        log_level = logging.ERROR #least verbose
    logging.basicConfig(level = log_level, format = FORMAT,
                        filename = log_file, encoding = 'utf-8')
    fre_logger.debug('log level set')


if __name__ == '__main__':
    fre()
