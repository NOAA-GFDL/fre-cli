#!/usr/bin/env python
import subprocess
import sys
import scripts
import intakebuilder
from intakebuilder import localcrawler
from scripts import gen_intake_gfdl
import fre
import intake

def func():
#    fre.frecatalog.buildCatalog()
#    print(intakebuilder.CSVwriter.getHeader())
    
#    print(intakebuilder.localcrawler())
    
    scripts.gen_intake_gfdl.main()

    print('\n',dir(intakebuilder))        
    
    print('\n',dir(intake))

    print('\n',dir(scripts))

    print('\n',dir(fre))    

if __name__ == '__main__':
    func()
