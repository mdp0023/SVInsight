import sys
import os

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

# set variables
project_name = 'Harris_County'
file_path = "/Users/matthewpreisser/Documents/Research/Codes/SVInsight"
api_key = os.environ.get('API_KEY')
geoids = ['48201']

# create instance
test = svi(project_name = project_name, 
    file_path = file_path, 
    api_key = api_key,
    geoids=geoids)

# set the boundary and year variables
boundary='bg'
year=2018
config_file = 'config'

# extract shapefile
export = test.boundaries_data(boundary, year)

# extract raw census data
test.census_data(boundary, 
                    year, 
                    interpolate=True,
                    verbose=True,
                    overwrite=False)

# # add variable
# test2.add_variable(boundary,
#                    year,
#                    'newvar',
#                    ['B03002_021E'])


# # print(test2.all_vars_eqs['MEDAGE']['description'])
# # test2.var_descriptions(['MEDAGE','PPUNIT'])

# configure run and calculate svi
test.configure_variables(config_file)
test.calculate_svi(config_file, boundary, year)





