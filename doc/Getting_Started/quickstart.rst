Getting Started
===============

Quickstart
----------

This is a quick guide to using SVInsight. In this demonstration, we show how to load and create the SVInsight object, determine an area of interest, set a boundary level (e.g., tract or block groups), download the necessary boundary and raw data, calculate input variables, and compute the social vulnerability estimate. 

First we load the SVInsight package, set the necessary variables, and create the SVInsight object. 

.. doctest::

    >>> from svinsight import SVInsight as svi
    >>> project_name = 'YOUR PROJECT NAME HERE'
    >>> file_path = "YOUR PARENT FOLDER HERE"
    >>> api_key = 'YOUR CENSUS API KEY HERE'
    >>> geoids = ['48453']
    >>> project = svi(project_name, file_path, api_key, geoids)

These variables create the instance of a project. Each have the following purpose: 

- ``project_name``: This is the name of your project. In this case, it's 'Travis_County_SVI'. The project name is used when saving files throughout the project.
- ``file_path``: This is the path to the parent folder where your project files will be stored. Replace "YOUR PARENT FOLDER HERE" with the actual path. Creating the SVInsight object automatically creates the necessary file structure needed for your project based on the ``file_path`` and ``project_name``. 
- ``api_key``: This is your Census API key. Replace 'YOUR CENSUS API KEY HERE' with your actual API key. You can obtain an API key from the `Census Bureau's developer page <https://www.census.gov/data/developers/data-sets.html>`_.
- ``geoids``: This is a list of geographic identifiers for the areas you're interested in. In this case, it's ['48453'], which represents Travis County, Texas. The necessary geographic identifiers for your state or county of interest can be obtained from this `FCC page <https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt>`_.  


Each instance of SVInsight can be seen as a standalone project for a constant study area. Within each project, the user can explore different vulnerability estimates based on different years or boundaries (e.g., block group versus tract). 

In this quickstart, we will examine a vulnerability estimate for Travis County using 2019 data at the block group level. 

.. doctest::

    >>> boundary = 'bg'
    >>> year = 2019
    >>> config_file = 'config_file'

The simplest workflow is as follows: 

(1) Extract boundaries 
(2) Extract Census data 
(3) Configure variables  
(4) Calculate vulnerability estimate 

.. doctest::

    >>> project.boundaries_data(boundary, year)
    >>> project.census_data(boundary, year)
    >>> project.configure_variables(config_file)
    >>> project.calculate_svi(config_file, boundary, year)

The output SVI .csv and .gpkg files built will be saved with the following file format: 

- folder location: ``{file_path}/{project_name}/{SVIs}/`` 
- file name: ``{project_name}_{year}_{boundadry}_{config_file}_svi``
 
More detailed examples of the complete functionality of SVInsight can be found under :doc:`Examples <../Examples/examples>`.