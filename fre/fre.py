"""
Main host file for FRE-CLI program scripts
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
2023-2024
principal click group for main/fre allows for subgroup functions to
be called via this script. I.e. 'fre' is the entry point
"""

from . import version, FORMAT

import click

from .lazy_group import LazyGroup

import logging
fre_logger = logging.getLogger(__name__)

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
                       "analysis": ".analysis.freanalysis.analysis_cli",
                       "sfollow": ".sfollow.fresfollow.sfollow_cli"},
    help = click.style(
        "'fre' is the main CLI click group. It houses the other tool groups as lazy subcommands.",
        fg = 'cyan')
)
@click.option( '-v', '--verbose', default = 0, required = False, count = True, type = int,
               help = "Increment logging verbosity from default (logging.WARNING) to logging.INFO. use -vv for logging.DEBUG. will be overridden by -q/--quiet" )
@click.option( '-q', '--quiet', default = False, required = False, is_flag = True, type = bool,
               help = "Set logging verbosity from default (logging.WARNING) to logging.ERROR, printing less output to screen. overrides -v[v]/--verbose" )
@click.option( '-l', '--log_file', default = None, required = False, type = str,
               help = 'Path to log file for all fre calls, the output to screen will still print with the path specified. ' + \
                      'If the log file already exists, it is appended to.' )
def fre(verbose = 0, quiet = False, log_file = None):
    '''
    entry point function to subgroup functions, setting global verbosity/logging formats that all
    other routines will utilize
    '''
    log_level = logging.WARNING # default
    if verbose == 1:
        log_level = logging.INFO # -v, more verbose than default
    elif verbose == 2:
        log_level = logging.DEBUG # -vv most verbose

    if quiet:
        log_level = logging.ERROR # least verbose

    base_fre_logger=fre_logger.parent
    base_fre_logger.setLevel(level = log_level)
    fre_logger.debug('root fre_logger level set')

    # check if log_file arg was used
    if log_file is not None:
        fre_logger.debug('creating fre_file_handler for fre_logger')
        fre_file_handler=logging.FileHandler(log_file,
                                             mode='a',encoding='utf-8',
                                             delay=False) # perhaps should revisit the delay=False bit

        fre_logger.debug('setting fre_file_handler logging format:')
        fre_log_file_formatter=logging.Formatter(fmt=FORMAT)
        fre_file_handler.setFormatter(fre_log_file_formatter)

        base_fre_logger.addHandler(fre_file_handler)
        fre_logger.info('fre_file_handler added to base_fre_logger') # first message that will appear in the log file if used
        
    fre_logger.debug('click entry-point function call done.')
    
if __name__ == '__main__':
    fre()
