
import sys
sys.path.append('/Users/matthewpreisser/Documents/Research/Codes/SVInsight')

# import package
from SVInsight import SVInsight as svi 
import os
import pytest
import geopandas as gpd

# set some initial value
project_name='test_proj'
file_path=os.getcwd()
api_key='test_api_key' 
geoids=['48453']


def test_svi():
    """Test that project can be created"""
    assert svi(project_name, file_path, api_key, geoids)

def test_svi_project_name():
    """Test that project name is string"""
    with pytest.raises(TypeError):
        svi(2, file_path, api_key, geoids)

def test_svi_file_path_exists():
    """Test that file path exists"""
    with pytest.raises(FileNotFoundError):
        svi(project_name, 'incorrect_file_path', api_key, geoids)

def test_svi_geoids_incorrect():
    """Test various scenarios of incorrect geoids"""
    with pytest.raises(ValueError):
        geos=[['123'],
              ['a','b','c'],
              [12345,12],
              ['12345','48']]
        for geo in geos:
            svi(project_name, file_path, api_key, geo)

def test_svi_geoids_correct():
    """Test various scenarios of correct geoids"""
    geos=[['12', '48'],
            ['12345','48256']]
    for geo in geos:
       assert svi(project_name, file_path, api_key, geo)


# develop a test project for single county
project_name = 'test_proj' 
file_path = os.path.dirname(os.path.realpath(__file__))
api_key = os.getenv('CENSUS_API_KEY')
geoids = ['48453']


@pytest.fixture
def project():
    return svi(project_name, file_path, api_key, geoids)

def test_single_county_project(project):
    """Test if a project file structure is created"""
    # test project instance
    assert project
    # test folder instances
    for loc in ['Boundaries','Variables', 'Data', 'Documentation', 'SVIs']:
        assert os.path.exists(os.path.join(project.file_path, loc))
    
boundaries = ['bg', 'tract']
years = [2015, 2020]
@pytest.mark.parametrize("boundary, year", [(b, y) for b in boundaries for y in years])
def test_boundaries_data(project, boundary, year, overwrite=True):
    """Test if boundaries are extracted appropriately for different boundareis and years """
    # Call the function with the test inputs
    result = project.boundaries_data(boundary, year, overwrite)

    # Check that the result is a GeoDataFrame
    assert isinstance(result, gpd.GeoDataFrame)

    # Check that the output file exists
    output_file = os.path.join(project.boundaries, f"{project.project_name}_{year}_{boundary}.gpkg")  # Replace this with the actual output file path
    assert os.path.isfile(output_file)




    # # set the boundary and year variables
    # # boundaries=['bg','tract']
    # # years=[2015,2020]
    # boundaries=['tract']
    # years=[2020]
    # config_file = 'config'

    # for boundary in boundaries:
    #     for year in years:

    #         # extract shapefile
    #         export = project.boundaries_data(boundary, year)

