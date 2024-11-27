"""
Main host file for FRE-CLI program scripts
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
2023-2024
principal click group for main/fre allows for subgroup functions to 
be called via this script. I.e. 'fre' is the entry point
"""

import click
from .lazy_group import LazyGroup

# Horrible way to turn xxxx.y into xxxx.0y
import importlib.metadata
version_unexpanded = importlib.metadata.version('fre-cli')
version_unexpanded_split = version_unexpanded.split('.')
if len(version_unexpanded_split[1]) == 1:
    version_minor = "0" + version_unexpanded_split[1]
else:
    version_minor = version_unexpanded_split[1]
version = version_unexpanded_split[0] + '.' + version_minor

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
                       "cmor": ".cmor.frecmor.cmor_cli"                      },
    help = click.style(
        "'fre' is the main CLI click group that houses the other tool groups as lazy subcommands.",
        fg='cyan')
)


@click.version_option(
    package_name = "fre-cli"
)

def fre():
    ''' entry point function to subgroup functions '''


if __name__ == '__main__':
    fre()
