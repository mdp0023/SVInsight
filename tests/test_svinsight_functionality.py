# Testing functionality of svinsight without requiring API key

# import package
from svinsight import SVInsight as svi 
import os
import pytest
import geopandas as gpd
import matplotlib.figure
import sys



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




##############################################################################################
# TESTS FOR MINOR PROJECT FUNCTIONALITY

# set some initial value with blank api_key
project_name='test_proj'
file_path=os.getcwd()
geoids=['48453']
api_key = ''


def test_svi():
    """Test that project can be created"""
    assert svi(f"{os.path.dirname(os.path.realpath(__file__))}/{project_name}", file_path, api_key, geoids)

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







##############################################################################################
# TESTS FOR MAJOR PROJECT FUNCTIONALITY
# create a generic test architecture
def run_svi_workflow(project_name, file_path, geoids, config, boundary, year, overwrite=False, varchange=False):
    """Run the svi workflow for a given project"""
    project = svi(project_name, file_path, api_key, geoids)

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
    output_file6 = os.path.join(project.documentation, f"{project.project_name}_{year}_{boundary}_{config}_{year}_{boundary}.xlsx")
    assert os.path.isfile(output_file4)
    assert os.path.isfile(output_file5)
    assert os.path.isfile(output_file6)

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


    # test figure plotting optinos
    # PLOT OPTION 1
    try:
        output_fig = project.plot_svi(plot_option=1, geopackages=[year, boundary, f"{config}_{year}_{boundary}", 'FA_SVI_Rank'])
        assert isinstance(output_fig, matplotlib.figure.Figure), "output_fig is not a matplotlib figure"
    except Exception as e:
        assert False, f"plot_svi, plot_option = 1, execution failed: {e}"

    # PLOT OPTION 2
    try:
        output_fig = project.plot_svi(plot_option=2, geopackages=[[year, boundary, f"{config}_{year}_{boundary}", 'FA_SVI_Rank'],[year, boundary, f"{config}_{year}_{boundary}", 'FA_SVI_Rank']])
        assert isinstance(output_fig, matplotlib.figure.Figure), "output_fig is not a matplotlib figure"
    except Exception as e:
        assert False, f"plot_svi, plot_option = 1, execution failed: {e}"

    # PLOT OPTION 3
    try:
        output_fig = project.plot_svi(plot_option=3, geopackages=[year, boundary, f"{config}_{year}_{boundary}"])
        assert isinstance(output_fig, matplotlib.figure.Figure), "output_fig is not a matplotlib figure"
    except Exception as e:
        assert False, f"plot_svi, plot_option = 1, execution failed: {e}"


    # remove all output files to reduce package space    
    os.remove(output_file3)
    os.remove(output_file4)
    os.remove(output_file5)
    os.remove(output_file6)


# develop a test project for single county
boundaries = ['bg', 'tract']
years = [2015, 2020]
@pytest.mark.parametrize("boundary, year", [(b, y) for b in boundaries for y in years])
def test_single_county_project(boundary, year, overwrite=False):
    """Using the given single county data, check workflow including variable configuration, calculating vulnerability indices, and plot creation"""
    """test creating and running a single county project for different years and boundaries"""
    run_svi_workflow(project_name='test_project_single_county' ,
                    file_path=os.path.dirname(os.path.realpath(__file__)),
                     geoids=['48453'],
                     config='config',
                     boundary=boundary, 
                     year=year, 
                     overwrite=overwrite)


# develop a test project for multiple counties
boundaries = ['bg', 'tract']
years = [2015, 2020]
@pytest.mark.parametrize("boundary, year", [(b, y) for b in boundaries for y in years])
def test_multiple_county_project(boundary, year, overwrite=False):
    """test creating and running a multiple counties project for different years and boundaries"""
    run_svi_workflow(project_name='test_project_multiple_counties' ,
                    file_path=os.path.dirname(os.path.realpath(__file__)),
                     geoids=['48453','21117'],
                     config='config', 
                     boundary=boundary, 
                     year=year, 
                     overwrite=overwrite)


# develop a test project for multiple states
boundaries = ['bg', 'tract']
years = [2015]
@pytest.mark.parametrize("boundary, year", [(b, y) for b in boundaries for y in years])
def test_multiple_states_project(boundary, year, overwrite=False):
    """test creating and running a multiple states project for different years and boundaries"""
    run_svi_workflow(project_name='test_project_multiple_states' ,
                    file_path=os.path.dirname(os.path.realpath(__file__)),
                     geoids=['25','44'],
                     config='config',  
                     boundary=boundary, 
                     year=year, 
                     overwrite=overwrite)


# develop a test project for single county, economic index
boundaries = ['bg']
years = [2017]
@pytest.mark.parametrize("boundary, year", [(b, y) for b in boundaries for y in years])
def test_single_county_economic_project(boundary, year, overwrite=False):
    """test creating and running a multiple states project for different years and boundaries"""
    run_svi_workflow(project_name='test_project_economic_index' ,
                    file_path=os.path.dirname(os.path.realpath(__file__)),
                     geoids=['48453'],
                     config='config',  
                     boundary=boundary, 
                     year=year, 
                     overwrite=overwrite, 
                     varchange=True)
