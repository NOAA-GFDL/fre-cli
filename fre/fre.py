"""
Main host file for FRE-CLI program scripts
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
2023-2024
"""

import click

from .lazy_group import LazyGroup

#############################################

"""
principal main fre click group allows for subcommand functions from subgroups to be called via through this script with 'fre' as the entry point
"""
@click.group(
    cls=LazyGroup,
    lazy_subcommands={"pp": ".pp.frepp.ppCli",
                      "catalog": ".catalog.frecatalog.catalogCli",
                      "list": ".list.frelist.listCli",
                      "check": ".check.frecheck.checkCli",
                      "run": ".run.frerun.runCli",
                      "test": ".test.fretest.testCli",
                      "yamltools": ".yamltools.freyamltools.yamltoolsCli",
                      "make": ".make.fremake.makeCli",
                      "app": ".app.freapp.appCli",
                      "cmor": ".cmor.frecmor.cmorCli"
                      },
    help=click.style("'fre' is the main CLI click group that houses the other tool groups as lazy subcommands.", fg='cyan')
)
@click.version_option(package_name="fre-cli", message=click.style("%(package)s | %(version)s", fg=(155,255,172)))
def fre():
    pass

#############################################

if __name__ == '__main__':
    fre()
