
import sys
sys.path.insert(0, '/Users/matthewpreisser/Documents/Research/Codes/SVInsight')

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



# create a generic test architecture
def run_svi_workflow(project, boundary, year, overwrite=True, varchange=False):
    # test project instance
    assert project
    # test folder instances
    for loc in ['Boundaries','Variables', 'Data', 'Documentation', 'SVIs']:
        assert os.path.exists(os.path.join(project.file_path, loc))
    
    # Call the function with the test inputs
    gpkg = project.boundaries_data(boundary=boundary, year=year, overwrite=overwrite)

    # Check that the result is a GeoDataFrame
    assert isinstance(gpkg, gpd.GeoDataFrame)

    # Check that the output file exists
    output_file = os.path.join(project.boundaries, f"{project.project_name}_{year}_{boundary}.gpkg")
    assert os.path.isfile(output_file)

    # check extraction of raw census data (if successful, returns nothing)
    try:
        project.census_data(boundary, year, interpolate=True, verbose=True, overwrite=overwrite)
    except Exception:
        assert False, "census_data execution failed"

    # check that the output files exists
    output_file1 = os.path.join(project.data, f"{project.project_name}_{year}_{boundary}_rawdata.csv")
    output_file2 = os.path.join(project.data, f"{project.project_name}_{year}_{boundary}_rawdata.gpkg")
    assert os.path.isfile(output_file1)
    assert os.path.isfile(output_file2)

    if varchange is True:
        # change variables to calculate an economic index
         # check configure
        try:
            project.configure_variables(f"{config}_{year}_{boundary}", include=['MDHSEVAL','PERCAP','QRICH'])
        except Exception:
            assert False, "configure_variables execution failed"

    else:
        # check configure
        try:
            project.configure_variables(f"{config}_{year}_{boundary}")
        except Exception:
            assert False, "configure_variables execution failed"

    # check if output files exist
    output_file3 = os.path.join(project.variables, f"{config}_{year}_{boundary}.yaml")
    assert os.path.isfile(output_file3)
    
    # check svi creation
    try:
        project.calculate_svi(config_file = f"{config}_{year}_{boundary}", boundary=boundary, year=year)
    except:
        assert False, "calculate_svi execution failed"

    # Check that output files exist 
    output_file4 = os.path.join(project.svis, f"{project.project_name}_{year}_{boundary}_{config}_{year}_{boundary}_svi.gpkg")
    output_file5 = os.path.join(project.svis, f"{project.project_name}_{year}_{boundary}_{config}_{year}_{boundary}_svi.csv")
    assert os.path.isfile(output_file4)
    assert os.path.isfile(output_file5)

    # read in geopackage and make sure the right variables are there and non all 0 or NaN
    svi_test = gpd.read_file(os.path.join(project.svis, f"{project.project_name}_{year}_{boundary}_{config}_{year}_{boundary}_svi.gpkg"))
    column_names=['FA_SVI_Unscaled',
                  'FA_SVI_Scaled',
                  'FA_SVI_Rank',
                  'FA_SVI_Percentile',
                  'RM_SVI_Rank',
                  'RM_SVI_Percentile']
    for column in column_names:
        assert column in svi_test.columns, f"Column {column} does not exist in DataFrame"
        assert not svi_test[column].isna().all(), f"All values in column {column} are NaN"
        assert not (svi_test[column] == 0).all(), f"All values in column {column} are 0"

# create fixture of project
@pytest.fixture
def project():
    return svi(project_name, file_path, api_key, geoids)

api_key = os.environ.get('API_KEY')

##############################################################################################
# develop a test project for single county
project_name = 'test_project_single_county' 
file_path = os.path.dirname(os.path.realpath(__file__))
geoids = ['48453']
boundaries = ['bg', 'tract']
years = [2015, 2020]
config='config'

@pytest.mark.parametrize("boundary, year", [(b, y) for b in boundaries for y in years])
def test_single_county_project(project, boundary, year, overwrite=False):
    """test creating and running a single county project for different years and boundaries"""
    run_svi_workflow(project, boundary, year, overwrite=overwrite)
##############################################################################################
 
##############################################################################################
# develop a test project for multiple counties
project_name = 'test_project_multiple_counties' 
file_path = os.path.dirname(os.path.realpath(__file__))
geoids = ['48453','21117']
boundaries = ['bg', 'tract']
years = [2015, 2020]
config='config'

@pytest.mark.parametrize("boundary, year", [(b, y) for b in boundaries for y in years])
def test_multiple_county_project(project, boundary, year, overwrite=False):
    """test creating and running a multiple counties project for different years and boundaries"""
    run_svi_workflow(project, boundary, year, overwrite=overwrite)
##############################################################################################

##############################################################################################
# develop a test project for multiple states
project_name = 'test_project_multiple_states' 
file_path = os.path.dirname(os.path.realpath(__file__))
geoids = ['25','44']
boundaries = ['bg', 'tract']
years = [2015]
config='config'

@pytest.mark.parametrize("boundary, year", [(b, y) for b in boundaries for y in years])
def test_multiple_states_project(project, boundary, year, overwrite=False):
    """test creating and running a multiple states project for different years and boundaries"""
    run_svi_workflow(project, boundary, year, overwrite=overwrite)
##############################################################################################

##############################################################################################
# develop a test project for single county, economic index
project_name = 'test_project_economic_index' 
file_path = os.path.dirname(os.path.realpath(__file__))
geoids = ['48453']
boundaries = ['bg']
years = [2017]
config='config'

@pytest.mark.parametrize("boundary, year", [(b, y) for b in boundaries for y in years])
def test_single_county_economic_project(project, boundary, year, overwrite=True):
    """test creating and running a multiple states project for different years and boundaries"""
    run_svi_workflow(project, boundary, year, overwrite=overwrite, varchange=True)
##############################################################################################