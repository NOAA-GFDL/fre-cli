# FRE Code Style Guide

Disclaimer: This style guide is still in development.

Follow these Style Guidelines when contributing to the `fre-cli` repository.

## Code Checklist

Checklist before requesting a review:

- [ ] I ran my code
- [ ] I tried to make my code readable
- [ ] I tried to comment my code
- [ ] I wrote a new test, if applicable
- [ ] I wrote new instructions/documentation, if applicable
- [ ] I ran pytest and inspected it's output
- [ ] I ran pylint and attempted to implement some of it's feedback
- [ ] No print statements; all user-facing info uses logging module

## General Documentation Tips

Here are some things to keep in mind when writing documentation:
 - Keep sentences short
 - Avoid the use of pronouns such as this, that, and it
 - Use the imperative mood for procedures
    - E.g. Instead of "You should install Conda" say “Install Conda”
 - Write in active voice rather than passive
 - Write objectively (minimize humor, jargon, idioms, etc)

Useful Resources:
 - https://docs.openstack.org/doc-contrib-guide/writing-style/general-writing-guidelines.html

## Inline Python Documentation Requirements

Document classes and functions with docstrings. These doctrings should contain field lists documenting arguments and
returns.  Field lists are sequences of fields marked up: `:fieldname: Field content`.  You do not need to document
click interface functions with field lists.

Document classes, variables and functions with type hinting.  It is encouraged to document click interface functions
with type hinting.  Type hinting is when you annotate functions and variables with the expected Python type.
Annotations are described in [PEP 3107](https://peps.python.org/pep-3107/).

Useful Resources
 - https://docs.python.org/3/library/typing.html
 - https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
 - https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#field-lists
 - https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html

This example shows how to properly document a class and two functions with docstrings containing field lists and type
hinting:

```python
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

def func_with_return_and_optional_param(a: int, c: List[int] = [1,2]) -> Any:
    """
    summary

    :param a: description
    :type a: int
    :param c: description, defaults to [1,2]
    :type c: list, optional
    :raises ValueError: description
    :return: description
    :rtype: type

    .. note:: This is a note
    .. warning:: This is a warning
    """

    if a > 10:
        raise ValueError("a is more than 10")
    return c

def simple_func(foo: str):
    """
    summary

    :param foo: description
    :type foo: str
    """

    pass
```
