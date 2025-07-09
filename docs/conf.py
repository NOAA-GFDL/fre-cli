# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'fre-cli'
copyright = '2024, NOAA-GFDL MSD Workflow Team'
author = 'NOAA-GFDL MSD Workflow Team'
# special thank you to Bennett Chang for intializing the fre-cli repository
release = '2025.04'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.apidoc']

templates_path = ['_templates']
exclude_patterns = ['fre/tests/test_files/ascii_files/*']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'renku'
#html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
