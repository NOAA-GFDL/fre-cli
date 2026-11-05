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
   are defined by:

.. code-block::

  &ReusableVariable Value

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
