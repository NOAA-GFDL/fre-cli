"""
Main host file for FRE-CLI program scripts
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
2023-2024
principal click group for main/fre allows for subgroup functions to 
be called via this script. I.e. 'fre' is the entry point
"""

import importlib.metadata

import click
from .lazy_group import LazyGroup

import logging
fre_logger = logging.getLogger(__name__)

# versioning, turn xxxx.y into xxxx.0y
version_unexpanded = importlib.metadata.version('fre-cli')
version_unexpanded_split = version_unexpanded.split('.')
if len(version_unexpanded_split[1]) == 1:
    version_minor = "0" + version_unexpanded_split[1]
else:
    version_minor = version_unexpanded_split[1]
version = version_unexpanded_split[0] + '.' + version_minor


@click.version_option(
    package_name = "fre-cli",
    version=version
)


# click and lazy group loading
@click.group(
    cls = LazyGroup,
    lazy_subcommands = {"pp": ".pp.frepp.pp_cli",
                       "catalog": ".catalog.frecatalog.catalog_cli",
                       "list": ".list.frelist.list_cli",
                       "check": ".check.frecheck.check_cli",
                       "run": ".run.frerun.run_cli",
                       "test": ".test.fretest.test_cli",
                       "yamltools": ".yamltools.freyamltools.yamltools_cli",
                       "make": ".make.fremake.make_cli",
                       "app": ".app.freapp.app_cli",
                       "cmor": ".cmor.frecmor.cmor_cli",
                       "analysis": ".analysis.freanalysis.analysis_cli"},
    help = click.style(
        "'fre' is the main CLI click group. It houses the other tool groups as lazy subcommands.",
        fg='cyan')
)
@click.option('-v', '--verbose', is_flag=True,
              default=False, help="set logging verbosity higher",
              required=False)
def fre(verbose):
    ''' entry point function to subgroup functions '''
    if verbose:
        logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    fre()
