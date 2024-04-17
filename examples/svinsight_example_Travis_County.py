import sys
sys.path.append('/Users/matthewpreisser/Documents/Research/Codes/SVInsight')


# import package
from SVInsight import SVInsight as svi 

# set variables
project_name = 'Travis_County'
file_path = "/Users/matthewpreisser/Documents/Research/Codes/SVInsight"
api_key = 'e2e25e1d5badb404a2c0ec61d1ea867f68ee4ecc'
geoids = ['48453']

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
export = test.boundaries_data(boundary, year, overwrite=True)

# # extract raw census data
# test.census_data(boundary, 
#                     year, 
#                     interpolate=True,
#                     verbose=True,
#                     overwrite=True)

# # # add variable
# # test2.add_variable(boundary,
# #                    year,
# #                    'newvar',
# #                    ['B03002_021E'])


# # # print(test2.all_vars_eqs['MEDAGE']['description'])
# # # test2.var_descriptions(['MEDAGE','PPUNIT'])

# # # configure run and calculate svi
# test.configure_variables(config_file)
# test.calculate_svi(config_file, boundary, year)





