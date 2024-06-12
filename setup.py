from setuptools import setup, find_namespace_packages
import setuptools_git_versioning
from setuptools_git_versioning import git_version

setup(
    name='fre-cli',
    version=git_version(),
    description='Command Line Interface for FRE commands',
    author='MSD Workflow Team, Bennett Chang, Dana Singh, Chris Blanton',
    author_email='oar.gfdl.workflow@noaa.gov',
    packages=find_namespace_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'setuptools-git-versionining>=2.0',
        'pyyaml',
        'pylint',
        'pytest',
        'jsonschema',
        'cylc-flow',
        'cylc-rose',
        'cdo',
        'metomi-rose'
    ],
    entry_points={
        'console_scripts': [
            'fre = fre.fre:fre',
        ],
    },
)
