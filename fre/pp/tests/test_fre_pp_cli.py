#!/usr/bin/env python3

from fre import fre
from fre import pp

from click.testing import CliRunner
runner = CliRunner()

#tests are structured in the manner of: 
#https://click.palletsprojects.com/en/8.1.x/testing/
#general intent for these tests is that each fre tool has 2 commandline tests:
#help, command does not exist

#Test list: 
#fre pp (covered in fre/tests, not fre/pp/tests)
#-- fre pp checkout
#-- fre pp configure-xml
#-- fre pp configure-yaml
#-- fre pp install
#-- fre pp run
#-- fre pp status 
#-- fre pp validate
#-- fre pp wrapper

