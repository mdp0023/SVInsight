import sys
sys.path.append('/Users/matthewpreisser/Documents/Research/Codes/SVInsight')


# from SVInsight import svi 
# import os 


from SVInsight import SVInsight as svi 
svi()



# # project_name = 'Travis_County'
# # file_path = "/Users/matthewpreisser/Documents/Research/Codes/SVInsight"
# # api_key = 'e2e25e1d5badb404a2c0ec61d1ea867f68ee4ecc'
# # geoids = ['48453','48201','21117']
# # boundary='bg'
# # year=2019

# # test = svi(project_name = project_name, 
# #     file_path = file_path, 
# #     api_key = api_key,
# #     geoids=geoids,
# #     boundary=boundary,
# #     year=year)

# # test.census_data(save_name='test',
# #                  interpolate=True,
# #                  verbose=True)



# project_name = 'Travis_County_2'
# file_path = "/Users/matthewpreisser/Documents/Research/Codes/SVInsight"
# api_key = 'e2e25e1d5badb404a2c0ec61d1ea867f68ee4ecc'
# geoids = ['48453','48201','21117']
# boundary='bg'
# year=2019

# test2 = svi(project_name = project_name, 
#     file_path = file_path, 
#     api_key = api_key,
#     geoids=geoids)

# # set the boundary and year variables
# boundary='bg'
# year=2019
# config_file = 'config'

# # extract shapefile
# export = test2.boundaries_data(boundary, year)

# # extract raw census data
# test2.census_data(boundary, 
#                     year, 
#                     interpolate=True,
#                     verbose=True)

# # add variable
# test2.add_variable(boundary,
#                    year,
#                    'newvar',
#                    ['B03002_021E'])



# # print(test2.all_vars_eqs['MEDAGE']['description'])
# # test2.var_descriptions(['MEDAGE','PPUNIT'])

# #test2.configure_variables(config_file)

# #test2.calculate_svi(config_file, boundary, year)





