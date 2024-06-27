from setuptools import setup, find_namespace_packages

def get_version_and_cmdclass(pkg_path):
    """Load version.py module without importing the whole package.
       Template code from miniver
    """
    import os
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("version", os.path.join(pkg_path, "_version.py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.get_cmdclass(pkg_path)


version, cmdclass = get_version_and_cmdclass(r"fre")


setup(
    name='fre-cli',
    version=version,
    cmdclass=cmdclass,
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
