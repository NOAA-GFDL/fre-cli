from setuptools import setup

setup(
    name='playtest',
    version='0.1.0',
    py_modules=['playtest'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'playtest = playtest:cli',
        ],
    },
)