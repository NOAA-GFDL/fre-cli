from setuptools import setup, find_namespace_packages

setup(
    name='fre-cli',
    version='2025.04',
    description='Command Line Interface for FRE commands',
    author='MSD Workflow Team',
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
        'xarray'
    ],
    extras_requires={
        "docs": ["sphinx==8.2.3",
                 "renku-spinx-theme==0.5.0",
                 "sphinx-rtd-theme==3.0.2"]
    },
    entry_points={
        'console_scripts': [
            'fre = fre.fre:fre',
        ],
    },
)
