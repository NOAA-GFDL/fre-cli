Helpful information and format recommendations for creating yaml files.

1. You can define a block of values as well as individual ``[key]: [value]``
   pairs:

.. code-block::

  section name:
    key: value
    key: value

2. ``[key]: [value]`` pairs can be made a list by utilizing a ``-``:

.. code-block::

  section name:
    - key: value
    - key: value

3. If you want to associate information with a certain listed element, follow
   this structure:

.. code-block::

  section name:
    - key: value
      key: value
    - key: value
      key: value

Where each dash indicates a list.

4. Yamls also allow for the capability of reusable variables. These variables
   can be defined using Jinja2 syntax:

.. code-block::

  fre_properties:
    ReusableVariable:  "Value"
    Variable:          "var2_{{ fre_properties.ReusableVariable }}"

When referencing another variable, the value must be a string. However, if the
new variable needs to be an integer or boolean for example, users can utilize
standard YAML tags. The fre-cli composes and resolves YAML variables using
"uwtools". For more information on how to use these tags and how uwtools
handles them, reference the uwtools documentation `here <https://uwtools.readthedocs.io/en/main/sections/user_guide/yaml/tags.html#custom-tags>`_.

5. Users can reference a previous key throughout the YAMLs.

In order to use them as a reference elsewhere in either the same or other
yamls, follow this Jinja2 structure example:

.. code-block::

  section1:
    key1: value1
    key2: value2

  section2:
    key3: "key3/{{ section1.key1 }}"

In this example, the variable ``key3`` value will be parsed as ``key3/value1``.
