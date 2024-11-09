# Testing functionality of svinsight that requires API key
# These tests require having a valid API key in the environment variable API_KEY
# the easiest way to do this is to create a .env file in the root directory of the project, and add the line:
    # API_KEY=your_api_key_here

# to view current environment variables:
    # printenv



# import package
from svinsight import SVInsight as svi 
import pytest
import sys
import os
import shutil


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




def get_api_key():
    api_key = os.getenv('API_KEY')
    assert api_key is not None, "CENSUS_API_KEY is not set"
    return api_key


@pytest.fixture
def project():
    project_name = 'test_proj_api'
    geoids = ['48453']
    api_key = get_api_key()
    this_directory = os.path.dirname(os.path.abspath(__file__))
    project =  svi(project_name, this_directory, api_key, geoids)

    yield project
    
    # Cleanup code: delete the folder where data is put
    data_directory = os.path.join(this_directory, project_name)  # Replace 'data_folder_name' with the actual folder name
    if os.path.exists(data_directory):
        shutil.rmtree(data_directory)


@pytest.mark.parametrize("boundary, year", [('tract', 2014), ('bg', 2022)])
def test_boundaries_census_pull(project, boundary, year):
    project.boundaries_data(boundary, year, overwrite=True)
    project.census_data(boundary, year, overwrite=True)

# @pytest.mark.parametrize("boundary, year", [('tract', 2014), ('tract', 2022), ('bg', 2014), ('bg', 2022)])
# def test_census_data(project, boundary, year):
#     project.census_data(boundary, year, overwrite=True)

