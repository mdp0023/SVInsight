.. SVInsight documentation master file, created by
   sphinx-quickstart on Wed Apr 10 16:47:20 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SVInsight
=========

**SVInsight** is a python package for calculating an exploratory social vulnerability index. This package calculates SVI using two methods: (1) an iterative factor analysis method and (2) a rank method, both of which have been heavily utilized in scholarly research. This package automates the creation and comparisons of indices using U.S. American Community Survey 5-Year Data (ACS5) at the block group or tract level. Users can customize which social, demographic, and economic variables are included in their own custom indices.

This package is a tool to efficiently calculate an exploratory estimate of social vulnerability for a given region. Social vulnerability is an incredibly complex and constantly evolving concept, and researchers, practitioners, and users of this software should always consult relevant peer-reviewed literature and local experts to validate findings.


.. figure:: all_time_steps.gif
   :align: center
   :alt: Gif of time-series for SVI estimates in Travis County, Texas

   Travis County SVI estimates from 2013 to 2021


Getting Started
###############
.. toctree::
   :maxdepth: 2
   
   Getting_Started/install
   Getting_Started/quickstart


Background
##########
.. toctree::
   :maxdepth: 1

   Background/background 
   Background/understanding
   Background/paper


User Guide
##########
.. toctree::
   :maxdepth: 2

   User_Guide/userguide 
   
API Reference
#############
.. toctree::
   :maxdepth: 1

   apiref/apiref 
   apiref/license


Examples
########
.. toctree::
   :maxdepth: 2

   Examples/examples 
   


Issues, Questions, and Contributions
####################################
.. toctree::
   :maxdepth: 2

   Contributions/contributions 


Acknowledgements
################
.. toctree::
   :maxdepth: 2

   Acknowledgements/acknowledgements 



.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
