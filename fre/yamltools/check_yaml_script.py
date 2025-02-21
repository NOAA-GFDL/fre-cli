'''
quick and cheap way to display yaml information to stdout.
'''


import logging
fre_logger = logging.getLogger(__name__)

import pprint
import yaml

from .combine_yamls_script import join_constructor as jc
yaml.add_constructor("!join", jc)

def yaml_check(yamlfile = None):
    ''' 
    uses python built-in pprint to readably-display info in a yamlfile on disk to stdout
    will de-alias references to anchors and use FRE's string-constructor, join (see above)
        yamlfile: string/Path to a yamlfile
    '''
    if yamlfile is None:
        raise ValueError(f'yamlfile arg is None- I need a yamlfile target!')

    if not Path(yamlfile).exists():
        raise FileExistsError(f'file {yamlfile} does not exist')
    
    with open( yamlfile,"r+", encoding='utf-8' ) as file_obj:

        #yaml_data=yaml.safe_load(file_obj) #Loader=yaml.Loader)
        yaml_data=yaml.load(file_obj, Loader=yaml.Loader)
        
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(yaml_data)



