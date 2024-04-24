import sys
import os
sys.path.insert(0, '/Users/matthewpreisser/Documents/Research/Codes/SVInsight')


# import package
from SVInsight import SVInsight as svi 
import matplotlib.pyplot as plt

# set variables
project_name = 'Travis_County'
file_path = "/Users/matthewpreisser/Documents/Research/Codes/SVInsight"
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
years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
config_file='SVI'

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

# print(test.all_vars_eqs['MEDAGE'])
# test.var_descriptions(['MEDAGE','PPUNIT'])

# # configure run and calculate svi
test.configure_variables(config_file)
test.calculate_svi(config_file, boundary, 2017)


# # MULTI YEARS
# for year in years:
#     # extract shapefile
#     export = test.boundaries_data(boundary, year, overwrite=False)

#     # # extract raw census data
#     test.census_data(boundary, year, interpolate=True,verbose=True,overwrite=False)

#     # # configure run and calculate svi
#     config_file='SVI'
#     test.configure_variables(config_file)
#     test.calculate_svi(config_file, boundary, year)
#     geopackages = [year, boundary, config_file, 'FA_SVI_Percentile']
#     figure = test.plot_svi(plot_option=1, geopackages=geopackages)
#     figure.savefig(f"{os.getcwd()}/Travis_County/Figures/{year}_{boundary}_{config_file}_FA_SVI_Percentile.png", dpi=300)


######## Plotting ########
# # plot svi single
# geopackages = [year, boundary, config_file, 'FA_SVI_Percentile']

# figure = test.plot_svi(plot_option=1,
#                        geopackages=geopackages)

#plot svi double
geopackages = [[2017, boundary, config_file, 'FA_SVI_Percentile'], [2017, boundary, config_file, 'RM_SVI_Percentile']]
figure = test.plot_svi(plot_option=2,
                       geopackages=geopackages)


# # plot svi complete
# geopackages = [2018, boundary, config_file]
# figure = test.plot_svi(plot_option=3,
#                        geopackages=geopackages)



plt.show()