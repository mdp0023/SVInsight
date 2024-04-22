import sys
import os
sys.path.insert(0, '/Users/matthewpreisser/Documents/Research/Codes/SVInsight')


# import package
from SVInsight import SVInsight as svi 
import matplotlib.pyplot as plt

# set variables
project_name = 'Travis_County'
file_path = "/Users/matthewpreisser/Documents/Research/Codes/SVInsight"
#api_key = 'e2e25e1d5badb404a2c0ec61d1ea867f68ee4ecc'
api_key = os.environ.get('API_KEY')
geoids = ['48453']

# create instance
test = svi(project_name = project_name, 
    file_path = file_path, 
    api_key = api_key,
    geoids=geoids)

# set the boundary and year variables
boundary='bg'
year=2017
config_file = 'config'

# extract shapefile
export = test.boundaries_data(boundary, year, overwrite=False)

# # extract raw census data
test.census_data(boundary, 
                    year, 
                    interpolate=True,
                    verbose=True,
                    overwrite=False)

# # # add variable
# # test2.add_variable(boundary,
# #                    year,
# #                    'newvar',
# #                    ['B03002_021E'])


# # # print(test2.all_vars_eqs['MEDAGE']['description'])
# # # test2.var_descriptions(['MEDAGE','PPUNIT'])

# # # configure run and calculate svi
# test.configure_variables(config_file, include=['MDHSEVAL','PERCAP','QRICH'])
# test.calculate_svi(config_file, boundary, year)

# plot svi single
# geopackages = [year, boundary, config_file, 'FA_SVI_Percentile']

# figure = test.plot_svi(plot_option=1,
#                        geopackages=geopackages)

# plot svi double
#geopackages = [[2018, boundary, config_file, 'FA_SVI_Rank'], [2018, boundary, config_file, 'RM_SVI_Rank']]
geopackages = [2018, boundary, config_file]
figure = test.plot_svi(plot_option=3,
                       geopackages=geopackages)




plt.show()