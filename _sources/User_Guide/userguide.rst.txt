.. currentmodule:: SVInsight.svi

User Guide
==========

Overview
--------

The basic workflow of `SVInsight` works as follows: 

1. Initialize the project class (:obj:`SVInsight`) with your project name, folder path, Census API key, and your study area.

2. Define the initial project configuration variables with a boundary (tract or block groups) and year.

3. Extract the necessary boundary geopackage using :meth:`SVInsight.boundaries_data`.

4. Extract the raw census data and fill in holes in the data using :meth:`SVInsight.census_data`.

5. Configure the run and calculate the SVI using :meth:`SVInsight.configure_variables` and :meth:`SVInsight.calculate_svi`. 


Below you will find the detailed user guide that walks through each of these steps, with additional options for project customization. `SVInsight` is supposed to be a flexible and exploratory estimator of various social vulnerability indices, and is therefore highly customizable within the framework of Factor Analysis and Rank Method methodologies. The User Guide below walks through the methods available for calculating SVIs. For a larger discussion on the Factor Analysis and Rank Method methodologies, please refer to the :doc:`Background </Background/background>` and  :doc:`Understanding Iterative Factor Analysis Results </Background/understanding>` pages. 


1. Initializing the Project
---------------------------

The first step to the project is importing :obj:`SVInsight` and setting the project `params.` Each instance of the class can be seen as a standalone project for the input geoids, where users can configure different runs based on years, boundaries, and variables of interest. In this User Guide we are using Travis_County, Texas as a working example.

.. doctest::

   >>> from svinsight import SVInsight as svi 
   >>> project_name = 'Travis_County'
   >>> file_path = "/User/Documents"
   >>> api_key = os.environ.get('API_KEY')
   >>> geoids = ['48453']
   >>> proj = svi(project_name, file_path, api_key, geoids)

These variables create the instance of a project. Each have the following purpose: 

- ``project_name``: This is the name of your project. In this case, it's 'Travis_County'. The project name is used when saving files throughout the project.
- ``file_path``: This is the path to the parent folder where your project files will be stored. Creating the SVInsight object automatically creates the necessary file structure needed for your project based on the ``file_path`` and ``project_name``. 
- ``api_key``: This is your Census API key. You can obtain an API key from the `Census Bureau's developer page <https://www.census.gov/data/developers/data-sets.html>`_.
- ``geoids``: This is a list of geographic identifiers for the areas you're interested in. In this case, it's ['48453'], which represents Travis County, Texas. The necessary geographic identifiers for your state or county of interest can be obtained from this `FCC page <https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt>`_. 

During the initialization, a series of folder is generated for storing the files created during a project. The folder locations and their intended contents are as follows:

- **Boundaries:** Will contain geopackages of the boundary areas based on the input geoids.
- **Data:** Where the raw census data csv and geopackages will be stored, in addition to other csv files that contain information about missing variables and how they were rectified. 
- **Documentation:** Will contain excel sheets of information pertinent to the factor analysis svi. 
- **SVIs:** Where the geopackages of SVIs will be stored.
- **Variables:** Where the configuration files will be stored.


2. Defining the Initial Project Configuration Variables
-------------------------------------------------------

The initial project configuration variables allows us to pull the appropriate boundary information. The boundary can be either `bg` or `tract` for block group or tract. Block groups and tracts are the two highest spatial resolutions that the US Census releases American Community Survey 5-Year estimates for. While block groups have a higher spatial resolution, they come with greater uncertainty in their estimates compared to tracts. More information can be found on the `Census website <https://www.census.gov/data/developers/data-sets/acs-5year.html>`_.

.. doctest::

   >>> boundary='bg'
   >>> year=2017
   >>> config_file = 'config'


.. figure:: census_divisions.jpeg
   :scale: 100 %
   :alt: Map showing the Census Divisions

   Visual representation of the different Census boundaries.


3. Extracting the Boundary 
--------------------------

With the boundary and year set, we can extract the necessary raw census data. In the :meth:`SVInsight.boundaries_data` method, there is a parameter ``overwrite`` which can be set to True or False. When True, if an existing geopackage for the given boundary and year is already found in the folder it will be overwritten. this method returns a geopandas dataframe. Furthermore, because Census boundaries include areas that may not have permanent populations (i.e., military installations, airports, national parks, etc.), a filter is automatically applied such that boundaries with less than a population of 75 are excluded from the analysis. 

.. doctest::

   >>> areas = proj.boundaries_data(boundary, year, overwrite=False)


4. Extract Raw Data and Filling Holes
-------------------------------------

The next step is to extract the raw census data using the :meth:`SVInsight.census_data` method. :obj:`SVInsight` starts has a default set of 27 social and economic variables of interest, which are detailed in the :ref:`variables` section. This method specifically pulls the raw data, and the variables themselves are calculated later. In this example, we are continuing to us the same boundary and year as the boundaries we just extracted, in order to produce a geopackaged version of raw data. Furthermore we have two additional parameters: ``interpolate`` and ``verbose``. **It is important to note** that the Census API will sometimes time out, and if Census data isn't being pulled, waiting a few seconds/minutes and re-running usually solves the problem.

.. doctest::

   >>> areas = proj.census_data(boundary, year, interpolate=True, verbose=True, overwrite=False)


- ``interpolate`` (bool): Census data, especially at the block group level, might have missing data points. Missing data can occur if there are not enough sample points in a given time period to accurately calculate the variable. In these instances, the holes must be filled to accurately calculate the SVIs. :obj:`SVInsight` can accomplish this two different ways, either with or without **interpolation**. When interpolation is True, missing values are determined by recalculating the median based on the detailed tables (e.g., the breakdown table of response ranges for a given variable) from the adjacent boundaries. Because interpolating isn't exact, any boundary that has less than 40 neighboring data points are not interpolated. For areas that are not interpolated, or if interpolation is set to False, holes are filled by taking the next available boundary value. For example, if a block group is missing a value it is replaced with the tract value, and if a tract value is missing it is filled with the county value.

- ``verbose`` (bool): When set to True, two additional csv values are saved in the Data folder that highlight which locations had holes that needed to be filled and the methodology in which it is filled (_missing_values.csv). If there happens to be an entire column that is missing information, the next highest available boundary is used to fill the entire variable (_missing_columns.csv). 

Similar to the :meth:`SVInsight.boundaries_data` method, there is an overwrite parameter as well. 



5. Configuring and Calculating SVI
----------------------------------

Finally, the :meth:`SVInsight.configure_variables` and :meth:`SVInsight.calculate_svi` methods are used to configure and run the SVI calculation.

.. doctest::

   >>> proj.configure_variables(config_file, exclude=None, include=None, inverse_vars=['PERCAP', 'QRICH', 'MDHSEVAL'])
   >>> proj.calculate_svi(config_file, boundary, year)


Configure Variables
^^^^^^^^^^^^^^^^^^^

This method prepares the information that will be included in the SVI calculation. This method is useful if you are interested in creating multiple different scenarios of SVI. For example, in some runs you may be interested in all 27 variables, while in others you may only want to include economic related variables. By creating a configuration file for each type of run, each SVI will be saved with the config_name associated with it for easier access and comparison. There are four main parameters of the :meth:`SVInsight.configure_variables` method: 

1. ``config_file`` (str): The name given to the configuration file

2. ``exclude`` (list): In order to remove a variable from the original list of 27, this parameter accepts a list of variables the user would like to exclude from the configuration.

3. ``include`` (list): the opposite of exclude, in that this parameter will remove all variables except those in this list. An exclude and an include parameter value cannot be given.

4. ``inverse_vars`` (list): Certain variables have an inverse relationship with vulnerability. For example, household with a higher per capita income, make over $250,000 annually, and/or have a higher median housing value are less vulnerable. The list of variables passed to inverse_vars are flipped to capture these dynamics. This parameter defaults to this list of three variables, and users can feel free to pass their own list of variables that they believe to be inversely related. 


Calculate  SVI
^^^^^^^^^^^^^^

With the configuration file set, the final SVI can be calculated. The output geopackage and CSV files will have each variable that is within the configuration file as well as the following SVI variables: 

- FA_SVI_Unscaled: The factor analysis method SVI estimate that is unscaled 
- FA_SVI_Scaled: The factor analysis method SVI estimate that is scaled 0 to 1
- FA_SVI_Percentile: The factor analysis method SVI estimate percentile
- FA_SVI_Rank: The factor analysis method SVI estimate rank
- RM_SVI_Percentile: The rank method SVI estimate percentile
- RM_SVI_Rank: The rank method SVI estimate rank

It is important to remember that **SVI estimates are exploratory and relative.** That means that SVI values' accuracy is dependent on the configuration of the run for a given location and only relative to within that study area.

6. Examine Variables
--------------------

An additional method to investigate variables is the :meth:`SVInsight.var_descriptions` method. Given a list of variables, the description can be printed. Similarly, users can access the variables based on the instance of the project to see the long description as well as the raw census variables that make up the numerator and denominator of the variable. Both methods below will print similar information.

.. doctest::

   >>> print(proj.all_vars_eqs['MEDAGE'])
   >>> proj.var_descriptions(['MEDAGE'])




7. Customizing Variables
------------------------

Users can also define their own variables using the :meth:`SVInsight.var_descriptions` method. If a user is interested in defining an additional variable this would need to be run before the configuration file is produced, which would automatically include the new variable in the calculated SVI (unless placed on the excluded list).

.. doctest::

   >>> proj.add_variable(boundary, year, name, num, den: list = [1], description: str = None)


The method's parameters are as follows (boundary and year the same as before):

- ``name`` (str): the abbreviated name of the variable
- ``num`` (list): the list of Census raw data variables that make up the sum of the numerator
- ``den`` (list): the list of Census raw data variables that make up the sum of the denominator
- ``description`` (str): An option string description of what the variable is


8. Plotting
-----------

There is also a simple plotting method, :meth:`SVInsight.plot_svi`, to quickly plot a few example plots. There are three options for plotting: 

Plot option 1: Single percentile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
With plot_option equal to 1, a single SVI will be plotted based on a given year, boundary, configuration file, and variable name. While the variable name can be any existing variable within the geopackage, it will automatically default to plotting as a percentile because of the relative nature of the SVI calculation and it is **most appropriate to analyze calculated SVIs in terms of their rank/percentile.** 

.. doctest::

   >>> import matplotlib.pyplot as plt
   >>> geopackages = [2017, boundary, config_file, 'FA_SVI_Percentile']
   >>> figure = proj.plot_svi(plot_option=1, geopackages)
   >>> plt.show()

.. figure:: single_plot.png
   :scale: 75 %
   :alt: Map showing SVI for 2017 Travis County

   2017 Block Group Social Vulnerability Estimate for Travis County using Factor Analysis method



Plot option 2: Double percentile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
With plot_option equal to 2, two different SVIs can be plotted next to each other for a visual comparison. These could be from the same geopackage comparing the factor analysis and rank methods, or two different configurations, two different boundaries, etc. The geopackages input should be a nested list in the same format as plot_option 1.

.. doctest::

   >>> geopackages = [[2017, boundary, config_file, 'FA_SVI_Percentile'], [2018, boundary, config_file, 'FA_SVI_Percentile']]
   >>> figure = proj.plot_svi(plot_option=2, geopackages)
   >>> plt.show()

.. figure:: double_plot.png
   :scale: 75 %
   :alt: Map showing SVI for 2017 and 2018 Travis County

   2017 and 2018 Block Group Social Vulnerability Estimate for Travis County using Factor Analysis method



Plot option 3: Full comparison
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When plot_option is equal to 3, a more detailed comparison is calculated that will produce a difference plot and calculate a linear regression. Because the difference map and linear regression require the same set of input geoids (i.e., the same locations in the geopackage), it is currently required that the variables come from the same geopackage, and its intended purpose is to therefore compare the differences between the Factor Analysis and Rank Method methodologies that have the same configuration. The geopackages input should be formatted as follows: [year, boundary, config]. If a variable option is passed it is ignored. The additional plots show the following information:

- Difference plot: Shows the The FA_SVI_Rank minus the RM_SVI_Rank to highlight areas where the factor analysis method is under (negative) and over (positive) predicting SVI rank when compared to the rank method. 
- Linear Regression: Shows linear correlation between factor analysis and rank method SVI estimates and automatically computes an r-squared value with p-value, 95% confidence interval, and 95% prediction interval.

.. doctest::

   >>> geopackages = [2018, boundary, config_file]
   >>> figure = proj.plot_svi(plot_option=3, geopackages)
   >>> plt.show()


.. figure:: complete_plot.png
   :scale: 75 %
   :alt: Map showing SVI comparison for 2018 Travis County (factor analysis method versus rank method)

   Comparison between factor analysis and rank methods: 2018 Block Group Social Vulnerability Estimate for Travis County 



