from pathlib import Path

from bs4 import BeautifulSoup 
import yaml


class XML():
    
    def __init__(self, xmlfile: str|Path):

        self.xmlfile = Path(xmlfile)

        if not self.xmlfile.exists():
            raise IOError(f"Cannot find XML file {xmlfile}")
        
        with open(xmlfile, "r") as openedfile:
            self.soup = BeautifulSoup(openedfile, "lxml-xml")


    def get_key(self, tagid: str, tagobj= None):

        if tagobj is None:
            tagobj = self.soup
        
        tagid = tagobj.get(tagid)

        if tagid is not None:
            tagid = tagid.strip()
            if tagid:
                return tagid

        return None


    def find_all(self, tag: str, soup = None, search_name: str = None):

        if soup is None:
            soup = self.soup

        args = [tag]
        if search_name is not None:
            args.append({"name": search_name})

        tagobjs = soup.find_all(*args)
        
        return tagobjs
        

    def get_tag(self, soup = None):

        if soup is None:
            soup = self.soup    
    
        tagobjs = soup.find_all(tags)

        if not tagobjs:
            return None

        return tagobjs
               
        
    def get_tag(self, tag, soup = None, tagid: str = None):

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
