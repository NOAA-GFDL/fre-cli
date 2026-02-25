Guide
----------
1. Using the main branch of the fre-workflows repository: 

.. code-block::

  # Load cylc and FRE
  module load cylc
  module load fre/foo2

  # Clone fre-workflows repository into ~/cylc-src/[experiment name]__[platform name]__[target name]
  fre pp checkout -e [experiment name] -p [platform] -t [target]

  # Create/configure the combined yaml file, rose-suite.conf, and any necessary rose-app.conf files
  fre pp configure-yaml -y [model yaml file] -e [experiment name] -p [platform] -t [target]

  # Validate the rose experiment configuration files
  fre pp validate -e [experiment name] -p [platform] -t [target]

  # Install the experiment
  fre pp install -e [experiment name] -p [platform] -t [target]

  # Run the experiment
  fre pp run -e [experiment name] -p [platform] -t [target]

Users can also run all fre pp subtools in one command:

.. code-block::

  # Load cylc and FRE
  module load cylc
  module load fre/foo2

  # Run all of fre pp
  fre pp all -e [experiment name] -p [platform] -t [target] -y [model yaml file]

2. Specifying a certain branch of the fre-workflows repository

.. code-block::

  # Load cylc and FRE
  module load cylc
  module load fre/foo2

  # Clone fre-workflows repository into ~/cylc-src/[experiment name]__[platform name]__[target name]
  fre pp checkout -e [experiment name] -p [platform] -t [target] -b [branch or tag name]

  # Create/configure the combined yaml file, rose-suite.conf, and any necessary rose-app.conf files
  fre pp configure-yaml -y [model yaml file] -e [experiment name] -p [platform] -t [target]

  # Validate the rose experiment configuration files
  fre pp validate -e [experiment name] -p [platform] -t [target]

  # Install the experiment
  fre pp install -e [experiment name] -p [platform] -t [target]

  # Run the experiment
  fre pp run -e [experiment name] -p [platform] -t [target]

To run all fre pp subtools in one command:

.. code-block::

  # Load cylc and FRE
  module load cylc
  module load fre/foo2

  # Run all of fre pp
  fre pp all -e [experiment name] -p [platform] -t [target] -y [model yaml file] -b [branch or tag name]
