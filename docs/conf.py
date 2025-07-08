# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


## this is for document building in readthedocs only.
#import sys
#from pathlib import Path
#sys.path.insert( 0,
#                 str(Path('.').resolve()) )


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Fre-Cli'
copyright = '2024, Bennett Chang'
author = 'Bennett Chang'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.apidoc']

#templates_path = ['_templates']
exclude_patterns = ['fre/tests/test_files/ascii_files/*']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'renku'
#html_theme = 'sphinx_rtd_theme'
#html_static_path = ['_static']
