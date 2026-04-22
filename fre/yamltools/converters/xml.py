from pathlib import Path

from bs4 import BeautifulSoup 
import yaml


class XML():
    
    def __init__(self, xmlfile: str|Path):

        self.xmlfile = Path(xmlfile)
        with open(xmlfile, "r") as openedfile:
            self.soup = BeautifulSoup(openedfile, "lxml-xml")


    def get_key(self, tagobj, tagid):

        tagid_value = tagobj.get(tagid)

        if tagid_value is not None:
            tagid_value = tagid_value.strip()
            if tagid_value:
                return tagid_value

        return None

    
    def get_tag(self, soup, tag, tagid: str = None):

        tagobj = soup.find(tag)

        if tagobj is None:
            return None
        
        if tagid is not None:
            return self.get_key(tagobj, tagid)
        
        tagstr = tagobj.text.strip()
        if tagstr:
            return tagstr

        return None

    
    def make_list(self, tag_value: str, split_token: str = None):

        if tag_value is None:
            return None
        
        return [val.strip() for val in tag_value.split(split_token)]
