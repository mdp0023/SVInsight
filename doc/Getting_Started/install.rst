Install
=======
`SVInsight` has been tested with Python 3.9 through 3.12. It also requires the following dependencies: `census <https://pypi.org/project/census/>`_, `factor_analyzer <https://pypi.org/project/factor-analyzer/>`_, `geopandas <https://geopandas.org/en/stable/>`_,  `numpy <https://numpy.org/install/>`_, `pandas <https://pandas.pydata.org/docs/getting_started/overview.html#>`_, `pytest <https://docs.pytest.org/en/7.1.x/getting-started.html>`_, `PyYAML <https://pypi.org/project/PyYAML/>`_, `scikit_learn <https://scikit-learn.org/stable/>`_, `openpyxl <https://pypi.org/project/openpyxl/>`_, and `matplotlib <https://matplotlib.org/stable/users/installing/index.html>`_.

Installation via *pip*
----------------------

To *pip*-install this package use the following command:

.. code-block:: console

   $ pip install SVInsight

`SVInsight` can then be imported into python:

.. code-block:: python

    >>> from svinsight import SVInsight as svi

SVInsight has dependencies that rely on gdal, which may require its own prior installation based on your operating system and coding environment. For example:

* On macOS:
 
  .. code-block:: console

      brew install gdal

* On Ubuntu:
 
  .. code-block:: console

      sudo apt-get install gdal-bin libgdal-dev

* On Windows:

  .. code-block:: console

      pip install gdal==<version> --find-links https://www.lfd.uci.edu/~gohlke/pythonlibs/

Installation via *conda*
------------------------

This package will be available from conda-forge soon.


