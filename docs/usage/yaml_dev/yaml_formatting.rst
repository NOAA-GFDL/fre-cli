Yaml Formatting
----------
Helpful information and format recommendations for creating yaml files.

1. You can define a block of values as well as individual ``[key]: [value]`` pairs:

.. code-block::

  section name:
    key: value
    key: value

2. ``[key]: [value]`` pairs can be made a list by utilizing a ``-``:

.. code-block::

  section name:
    - key: value
    - key: value

3. If you want to associate information with a certain listed element, follow this structure:

.. code-block::

  section name:
    - key: value
      key: value
    - key: value
      key: value

Where each dash indicates a list.

4. Yamls also allow for the capability of reusable variables. These variables are defined by:

.. code-block::

  &ReusableVariable Value

5. Users can apply a reusable variable on a block of values. For example, everything under "section" is associated with the reusable variable:

.. code-block::

  section: &ReusableVariable
    - key: value
      key: value
    - key: value

6. In order to use them as a reference else where in either the same or other yamls, use ``*``:

.. code-block:: 

  *ReusableVariable

7. If the reusable variable must be combined with other strings, the **`!join`** constructor is used. Simplified example:

.. code-block:: 

  &name "experiment-name"
  ...
  pp_dir: !join [/archive/$USER/, *name, /, pp]

In this example, the variable ``pp_dir`` will be parsed as ``/archive/$USER/experiment-name/pp``.
