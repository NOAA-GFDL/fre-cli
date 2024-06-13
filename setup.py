import subprocess

def get_git_version():
  try:
    # Get the latest tag using git describe
    output = subprocess.check_output(['git', 'describe', '--abbrev=0']).decode('utf-8').strip()
    # Split the output to get the tag (assuming valid format)
    return output.split('-')[0]
  except subprocess.CalledProcessError:
    # Fallback to a default version if git fails
    return "0.0.0"
from setuptools import setup, find_namespace_packages

setup(
    name='fre-cli',
    version=get_git_version(),
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
        'metomi-rose'
    ],
    entry_points={
        'console_scripts': [
            'fre = fre.fre:fre',
        ],
    },
)
