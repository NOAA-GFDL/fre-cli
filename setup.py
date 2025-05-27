from setuptools import setup, find_namespace_packages

setup(
    name='fre-cli',
    version='2025.03',
    description='Command Line Interface for FRE commands',
    author='MSD Workflow Team, Bennett Chang, Dana Singh, Chris Blanton',
    author_email='oar.gfdl.workflow@noaa.gov',
    packages=find_namespace_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'pyyaml',
        'pylint',
        'pytest',
        'jsonschema',
        'cylc-flow',
        'cylc-rose',
        'cdo',
        'cmor',
        'metomi-rose',
        'netcdf4',
        'xarray'
    ],
    entry_points={
        'console_scripts': [
            'fre = fre.fre:fre',
        ],
    },
)
