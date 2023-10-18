from setuptools import setup

setup(
    name='fre',
    version='0.1.0',
    py_modules=['fre'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'fre = fre:fre',
        ],
    },
)