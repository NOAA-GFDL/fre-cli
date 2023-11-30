from setuptools import setup, find_packages

setup(
    name='fre',
    version='0.1.0',
    description='Prototype for fre',
    author='Bennett Chang',
    author_email='Bennett.Chang@noaa.gov',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'fre = fre.fre:fre',
        ],
    },
)