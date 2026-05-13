from pathlib import Path

from bs4 import BeautifulSoup


class XML:
    """
    Base class to parse XML files and extract elements and key values using BeautifulSoup.
    """

    def __init__(self, xmlfile: str | Path):

        self.xmlfile = Path(xmlfile)
        if not self.xmlfile.exists():
            raise IOError(f"Cannot find XML file {xmlfile}")

        with open(xmlfile, "r", encoding="utf-8") as openedfile:
            xml_content = openedfile.read()

        self.soup = BeautifulSoup(xml_content, "lxml-xml")


    def get_attributes(self, attribute: str, element: dict, tolist: bool = False, fieldsep: str = ","):
        """
        Get attribute value from an XML element.  For example, 

        element = <source versionControl="git" root="http://github.com/NOAA-GFDL">
        get_attributes("root", element) returns "http://github.com/NOAA-GFDL"

        element = <component name="am5_phys" requires="fms rte-rrtmgp rte-ecckd">
        get_attributes("requires", element, tolist=True) returns ["fms", "rte-rrtmgp", "rte-ecckd"]
        """

        value = element.get(attribute)

        if value is not None:
            value = value.strip()
            if value:
                if tolist:
                    return [val.strip() for val in value.split(fieldsep)]
                return value

        return None


    def get_elements(self, element: str, xml_content, name: str = None, find_all: bool = True):
        """
        Get XML elements by tag name and optional attribute value.  For example,

        get_elements("component", soup) returns all <component> blocks in the XML.
        get_elements("component", soup, name="am5_phys") returns the <component> element block with name="am5_phys"
        """ 

        search_dict = {}
        if name is not None:
            search_dict["name"] = name

        find = xml_content.find_all if find_all else xml_content.find
        element = find(element, search_dict)

        return element


    def get_values(self, element, tolist: bool = False, fieldsep: str = ","):
        """
        Get value for an XML element.  For example, 

        element = <cppDefs> -DDEBUG -Iinclude</cppDefs>, 
        get_values(element, tolist=True) returns ["-DDEBUG", "-Iinclude"]
        """

        value = element.text.strip()

        if value:
            if tolist:
                if fieldsep is None:
                    return value.split()
                return [val.strip() for val in value.split(fieldsep)]
            return value

        return None