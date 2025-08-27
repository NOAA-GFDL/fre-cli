# FRE Code Style Guide

Follow these Style Guidelines when contributing to the `fre-cli` repository.

## General Documentation tips

Here are some things to keep in mind when writing documentation:
 - Keep sentences short
 - Avoid the use of pronouns (this, that, it, etc)
 - Use the imperative mood (the subject you is understood) for procedures
    - E.g. “Go to www.google.com”; “Install Conda”
 - Write in active voice rather than passive
 - Write objectively (do not include humor, jargon, idioms, etc)

Useful Resources:
 - https://docs.openstack.org/doc-contrib-guide/writing-style/general-writing-guidelines.html

## Inline Python Documentation Requirements

Document classes and functions with field lists for all Python files. You do not need to document click interface
functions with field lists.

Document classes, variables and functions with type hinting.  It is encouraged to document click interface functions
with type hinting

Useful Resources
 - https://docs.python.org/3/library/typing.html
 - https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
 - https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#field-lists
 - https://www.woolseyworkshop.com/2020/07/17/documenting-python-programs-with-sphinx/#CreatingASamplePythonProgram
 - https://github.com/NilsJPWerner/autoDocstring/blob/HEAD/docs/sphinx.md
 - https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
 - https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html#restructured-text-rest-and-sphinx-cheatsheet

An Example:

```
from typing import Any, List, ClassVar

class MyClass(object):
    """
    Description for class

    :cvar str var3: description
    :ivar str var1: description, initial value: par1
    :ivar str var2: description, initial value: par2
    """

    var3: ClassVar[str] = "I am a class variable" # class variable

    def __init__(self, par1: int, par2: int):
        self.var1 = par1 # instance variables
        self.var2 = par2

def abc(a: int, c: List[int] = [1,2]) -> Any:
    """
    summary

    :param a: description
    :type a: int
    :param c: description, defaults to [1,2]
    :type c: list, optional
    :raises AssertionError: description
    :return: description
    :rtype: type

    .. note:: This is a note
    .. warning:: This is a warning
    """

    #this is an example of type hinting a variable
    child: bool
    if a < 18:
        child = True
    else:
        child = False

    if a > 10:
        raise AssertionError("a is more than 10")
    return c

def func1(foo: str):
    """
    summary

    :param foo: description
    :type foo: str
    """

    print(foo)
```
