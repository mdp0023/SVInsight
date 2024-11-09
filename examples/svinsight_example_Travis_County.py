import sys
import os

# This package comes with initial Census boundaries and data for Travis County, TX
# With overwrite=False, the package will not download the data again 
# Therefore, an empty api_key will work for this example
# However, to download the data, you will need to get an API key from the US Census Bureau


# Get the directory that contains this file
this_directory = os.path.dirname(os.path.abspath(__file__))

# one level up 
dir1 = os.path.dirname(this_directory)
# two levels up 
dir2 = os.path.dirname(os.path.dirname(this_directory))

# Add the root directory to sys.path
sys.path.insert(0, this_directory)
sys.path.insert(0, dir1)
sys.path.insert(0, dir2)


# import package
from svinsight import SVInsight as svi 
import matplotlib.pyplot as plt

# set variables
project_name = 'Travis_County'
file_path = dir1
# api_key = os.environ.get('API_KEY')
api_key=''
geoids = ['48453']

# create instance
test = svi(project_name = project_name, 
    file_path = file_path, 
    api_key = api_key,
    geoids=geoids)

# set the boundary and year variables
boundary='bg'
year=2017
years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
config_file='SVI'

# extract shapefile
export = test.boundaries_data(boundary, year, overwrite=False)


# MULTI YEARS
for year in years:
    # extract shapefile
    export = test.boundaries_data(boundary, year, overwrite=False)

    # # extract raw census data
    test.census_data(boundary, year, interpolate=True,verbose=True,overwrite=False)

    # # configure run and calculate svi
    config_file='SVI'
    test.configure_variables(config_file)
    test.calculate_svi(config_file, boundary, year)
    geopackages = [year, boundary, config_file, 'FA_SVI_Percentile']
    figure = test.plot_svi(plot_option=1, geopackages=geopackages)
  

######## Plotting ########
# # plot svi single
geopackages = [year, boundary, config_file, 'FA_SVI_Percentile']

figure = test.plot_svi(plot_option=1,
                       geopackages=geopackages)

#plot svi double
geopackages = [[2017, boundary, config_file, 'FA_SVI_Percentile'], [2017, boundary, config_file, 'RM_SVI_Percentile']]
figure = test.plot_svi(plot_option=2,
                       geopackages=geopackages)


# plot svi complete
geopackages = [2018, boundary, config_file]
figure = test.plot_svi(plot_option=3,
                       geopackages=geopackages)



plt.show()