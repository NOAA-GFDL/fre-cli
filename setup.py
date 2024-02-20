from setuptools import setup, find_packages

setup(
    name='fre-cli',
    version='0.1.0',
    description='Command Line Interface for FRE commands',
    author='Bennett Chang',
    author_email='Bennett.Chang@noaa.gov',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'pyyaml',
        'jsonschema',
        'metomi-rose',
    ],
    entry_points={
        'console_scripts': [
            'fre = fre.fre:fre',
        ],
    },
)
