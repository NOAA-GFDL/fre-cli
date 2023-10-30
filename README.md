# FRE-CLI-Prototype
Prototype of future FMS Runtime Environment (FRE) CLI using Python's Click Lib

## Usage
* Need to set up Conda environment first and foremost
    - going to need Conda for python
    - need to pip install:
        - click
        - setuptools
    - using `setup.py`, must ensure that it is written in accordance with `fre.py` and `pip install --editable .` (these instructions are better explained in `/pdf_guides/Setuptools Integration -- Click Documentation (8.1.x).pdf`)
        - this will allow `fre.py` to be ran with `fre` in the command line instead of `python fre.py`
        - run `pip install .` to install packages from `setup.py`
* Enter commands and follow `--help` messages for guidance