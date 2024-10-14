
import os 
import csv
import copy
import shutil
# import zipfile
import numpy as np
import requests
import pandas as pd
# from ftplib import FTP
import geopandas as gpd
from census import Census
import concurrent.futures
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib as mpl
from concurrent.futures import ThreadPoolExecutor
from sklearn.preprocessing import MinMaxScaler
from factor_analyzer import FactorAnalyzer
import yaml
from scipy.stats import pearsonr
import scipy.stats as stats

from .census_variables import setup_census_variables

# current structure:
    # Each instance of class is a standalone project for a given study area.
    # A user can run different boundaries (tract or bg) and years within a single project
    # Will have a method to generate a .yaml file to save the variables (configuration) of a run 
        # will also have methods (or ability within this function) to change variable instances 

    # SVI outputs will have both factor analysis method and rank (CDC) method in one shapefile (easier comparison)
        # Also include all calcualted variables in the SVI output - easier to keep track and removes an unnecessary intermediary 



class SVInsight:
    """A class to calculate a Social Vulnerability Index."""

    @staticmethod
    def _validate_value(value, valid_options, value_name):
        """
        Validates a value against a list of valid options.

        Args:
            value (Any): The value to be validated.
            valid_options (List[Any]): A list of valid options.
            value_name (str): The name of the value being validated.

        Raises:
            ValueError: If the value is not in the list of valid options.

        Returns:
            None
        """
        if value not in valid_options:
            options_str = ', '.join(valid_options)
            raise ValueError(f"Invalid {value_name}. Must be one of: {options_str}.")
        
    @staticmethod
    def _validate_format(value, type, value_name):
        """
        Validates the format of a given value.

        Parameters:
        value (any): The value to be validated.
        type (type): The expected type of the value.
        value_name (str): The name of the value being validated.

        Raises:
        TypeError: If the value is not of the expected type.

        Returns:
        None
        """
        if not isinstance(value, type):
            raise TypeError(f"Invalid {value_name}. Must be type {type}.")

    @staticmethod
    def _geoid_format(geoids):
        """
        Validates the format of a list of GEOIDs.

        Args:
            geoids (list): A list of GEOIDs to be validated. Each GEOID must be length 2 or 5.

        Raises:
            ValueError: If the GEOIDs are not all of the same length, either 2 or 5.

        Returns:
            None
        """
        for geoid in geoids:
            if  geoid is int:
                raise ValueError('All GEOIDS must be string.')
        lengths = {len(geoid) for geoid in geoids}
        if len(lengths) > 1 or (list(lengths)[0] not in [2, 5]):
            raise ValueError("All GEOIDs must be of the same length, either 2 or 5.")
                

    def __init__(self, project_name: str, file_path: str, api_key: str, geoids: list[str]):
        """
        Initialize the SVInsight class.

        :param project_name: The name of the project. Will be used in file structure and names of saved files.
        :type project_name: str
        :param file_path: The file path where the project will be saved.
        :type file_path: str
        :param api_key: The Census API key for accessing data.
        :type api_key: str
        :param geoids: A list of geographic identifiers. Must all be either length 2 or 5.
        :type geoids: list[str]

        :raises FileNotFoundError: If the file path does not exist.
        :raises ValueError: If the GEOIDs are not all of the same length, either 2 or 5.
        :raises TypeError: If a value is not of the expected type.
        """
        # Determine if file path exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File path '{file_path}' does not exist.")
        
        # Set variable instances (inputs)
        self.project_name = project_name
        self.file_path = os.path.join(file_path, project_name)
        self.api_key = api_key
        self.geoids = geoids

        # set variable instances (defaults)
        self.low_pop_filter = 75        # boundaries to exlude 
        self.min_iterp_neighbors = 40   # minimum number of neighbors needed to interpolate holes

        # setup instances of Census variables
        self.all_vars_eqs, self.all_vars = setup_census_variables()

        # Validate Variables
        self._validate_format(project_name, str, 'project_name')
        self._validate_format(file_path, str, 'file_path')
        self._validate_format(api_key, str, 'api_key')
        self._validate_format(geoids, list, 'geoids')
        self._geoid_format(geoids)

        # Create file structure
        os.makedirs(self.file_path, exist_ok=True)
        folders = ['Boundaries','Variables', 'Data', 'Documentation', 'SVIs']
        for folder in folders:
            os.makedirs(os.path.join(self.file_path, folder), exist_ok=True)
            self.__dict__[folder.lower()] = os.path.join(self.file_path, folder)

        
    ###################################################
    # PUBLIC METHODS
    ###################################################

    # Method to pull block groups or tract shapefiles
    def boundaries_data(self, boundary: str = 'bg', year: int = 2019, overwrite: bool = False) -> gpd.GeoDataFrame:
        """
        Pulls block group or tract data from the Census FTP site.

        :param boundary: The type of boundary. Defaults to 'bg'. Acceptable values are 'bg', or 'tract'.
        :type boundary: str
        :param year: The year of the data. Defaults to '2019'.
        :type year: int
        :param overwrite: whether or not to overwrite an existing geopackage if it exists. Default is False
        :type overwrite: bool

        :return: The boundary data as a GeoDataFrame.
        :rtype: gpd.GeoDataFrame

        :raises ValueError: If the boundary type is invalid, the year is not between 2013 and 2022, or geoids not properly formatted.
        """
        
        # Validate Variables
        self._validate_value(boundary, ['bg', 'tract'], 'boundary')
        self._validate_value(year, [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], 'year')
        self._validate_format(boundary, str, 'boundary')
        self._validate_format(year, int, 'year')


        # If shapefile already exists, pass 
        if os.path.exists(os.path.join(self.boundaries, f"{self.project_name}_{year}_{boundary}.gpkg")) and overwrite is False:
            
            return gpd.read_file(os.path.join(self.boundaries, f"{self.project_name}_{year}_{boundary}.gpkg"))
        else:

            # create final output geodataframe
            output = gpd.GeoDataFrame()

            # helper functions
            def _download(year, state, boundary):
                """
                Downloads a shapefile from a remote FTP server, extracts it, and returns the boundary shapefile as a GeoDataFrame.

                Args:
                    year (int): The year of the shapefile. Valid options are from 2011 to 2021.
                    state (str): The state abbreviation.
                    boundary (str): The boundary type. Must be 'bg' or 'tract'

                Returns:
                    geopandas.GeoDataFrame: The boundary shapefile as a GeoDataFrame.
                """
               

                # create filenames
                filename = f"cb_{year}_{state}_{boundary}_500k"
                filename_dir = os.path.join(self.boundaries, filename)
                zipped_filename = f"{filename}.zip"
                zipped_dir = os.path.join(self.boundaries, zipped_filename)
                os.makedirs(filename_dir, exist_ok=True)
                
                #  # initiate FTP
                # ftp = FTP('ftp2.census.gov')
                # ftp.login()
                # ftp.cwd(f'geo/tiger/GENZ{year}/shp/')

                # # Open the file locally and write it to folder
                # print('opening binary')
                # with open(zipped_dir, "wb") as file:
                #     ftp.retrbinary(f"RETR {zipped_filename}", file.write)
                # print('opened binary')

                # Specify the URL of the file you want to download
                if year >= 2014:
                    url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/{zipped_filename}"
                elif year == 2013:
                    url = f"https://www2.census.gov/geo/tiger/GENZ{year}/{zipped_filename}"
               
                # Send a GET request to the URL
                response = requests.get(url, stream=True)

                # Check if the request was successful
                if response.status_code == 200:
                    # Open a local file with the same name as the remote file
                    with open(zipped_dir, 'wb') as file:
                        # Write the contents of the remote file to the local file
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)

                # Unzip the file
                shutil.unpack_archive(zipped_dir, filename_dir)
                # with zipfile.ZipFile(f"{zipped_dir}", 'r') as zip_ref:
                #     zip_ref.extractall(filename_dir)

                # Read the shapefile with geopandas
                boundary_shp = gpd.read_file(f"{filename_dir}/{filename}.shp")


                # remove the zipped and unzipped files
                os.remove(zipped_dir)
                shutil.rmtree(filename_dir)

                return boundary_shp


            # determine if we are pulling states or subset of counties 
            if len(self.geoids[0]) == 2:
                for geoid in self.geoids:
                    boundary_shp = _download(year, geoid, boundary)

                    # Concatenate output
                    output = pd.concat([output, boundary_shp], axis=0, join='outer')
            else:
                # Create a dictionary to store the locations
                geoid_dict = {}

                for geoid in self.geoids:
                    # Extract the first two numbers and last three numbers
                    prefix = geoid[:2]
                    suffix = geoid[2:]

                    # Check if the prefix already exists in the dictionary
                    if prefix in geoid_dict:
                        # Append the suffix to the existing list
                        geoid_dict[prefix].append(suffix)
                    else:
                        # Create a new list with the suffix
                        geoid_dict[prefix] = [suffix]

                for key, values in geoid_dict.items():
                    # keys are states
                    # values are list of counties from those states
                    boundary_shp= _download(year, key, boundary)

                    # Subset boundary_shp based on 'COUNTYFP' being in values
                    subset = boundary_shp[boundary_shp['COUNTYFP'].isin(values)]

                    # Concatenate output and subset
                    output = pd.concat([output, subset], axis=0, join='outer')

            # Save the output to a new folder
            output.to_file(os.path.join(self.boundaries, f"{self.project_name}_{year}_{boundary}.gpkg"))

            # Quit the FTP client
            #ftp.quit()

            return output
    

    # Method to pull census data and fill holes
    def census_data(self, boundary: str = 'bg', year: int = 2019, interpolate: bool = True, verbose: bool = False, overwrite: bool = False):
        """
        Pulls Census data for a specific boundary and year. The Census API can sometimes error out. Waiting a few seconds/minutes and re-running should solve the issue. 

        :param boundary: The boundary type to retrieve data for. Valid options are 'bg' (block group) and 'tract' (census tract).
        :type boundary: str
        :param year: The year of the Census data to retrieve. Valid options are from 2011 to 2021.
        :type year: int
        :param interpolate: Whether to interpolate missing data. Defaults to True. If year is before 2014, ignored and not-interpolated.
        :type interpolate: bool, optional
        :param verbose: Whether to display verbose output. Defaults to False.
        :type verbose: bool, optional
        :param overwrite: Whether to overwrite existing data. Defaults to False.
        :type overwrite: bool, optional

        :raises ValueError: If the boundary type is invalid or the year is not between 2013 and 2022.
        :raises FileNotFoundError: If the shapefile for the specified boundary and year does not exist.

        :return: None
        :rtype: None
        """
        # Validate Variables
        self._validate_value(boundary, ['bg', 'tract'], 'boundary')
        self._validate_value(year, [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], 'year')
        self._validate_format(boundary, str, 'boundary')
        self._validate_format(year, int, 'year')

        # If data already exists and overwrite is False, don't pull data 
        if os.path.exists(os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.gpkg")) and overwrite is False:
            pass
        else:

            # check if shapefile exists
            if not os.path.exists(os.path.join(self.boundaries, f"{self.project_name}_{year}_{boundary}.gpkg")):
                raise FileNotFoundError(f"{self.project_name}_{year}_{boundary}.gpkg not found. Run boundaries_data method prior to census_data.")
            else:
                shapefile = os.path.join(self.boundaries, f"{self.project_name}_{year}_{boundary}.gpkg")

            # Pull Census data
            data_df = self._census_pull(self.geoids, boundary, self.all_vars, self.api_key, year, self.low_pop_filter)
            # Fill missing columns
            data_df = self._fill_empty(data_df, boundary, self.geoids, self.api_key, year, verbose)

            # Relate to Geodataframe
            shapefile = gpd.read_file(shapefile)
            # create a new column with a shared 'key' to relate dataframes to
            if boundary == 'bg':
                shapefile['bg_fips'] = shapefile['GEOID']
                # merge geopandas shapefile with data_df shapefile
                data_df = data_df.merge(shapefile, on='bg_fips', how='left')
            elif boundary == 'tract':
                shapefile['tract_fips'] = shapefile['GEOID']
                # merge geopandas shapefile with data_df shapefile
                data_df = data_df.merge(shapefile, on='tract_fips', how='left')
            # convert data_df to geopandas
            data_df = gpd.GeoDataFrame(data_df, geometry=data_df['geometry'])
            # reset index of geodataframe
            data_df['index'] = data_df['GEOID'].astype(np.int64)
            data_df = data_df.set_index('index')

            # Fill in missing holes
            data_df = self._fill_holes(data_df, boundary, self.geoids, self.api_key, year, interpolate, verbose)

            # Save as csv and shapefile
            data_df.to_csv(os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.csv"))
            data_df.to_file(os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.gpkg"))


    # Method to inspect variable descriptions
    def var_descriptions(self, vars: list = None):
        """
        Print the descriptions of the variables.

        :param vars: Optional. List of variables to print descriptions for. If not provided, descriptions for all variables will be printed.
        :type vars: list

        :raises ValueError: If any variable in `vars` is not an available variable.

        :return: None
        :rtype: None
        """

        # Raise exception if var in vars not an available variable
        if vars is not None:
            for var in vars:
                self._validate_value(var, list(self.all_vars_eqs.keys()), var)

        if vars is None:
            vars = list(self.all_vars_eqs.keys())
        for var in vars:
            print(f"{var}: {self.all_vars_eqs[var]['description']}")
        

    # Method to add a variable
    def add_variable(self, boundary: str, year: int, name:str, num: list, den: list = [1], description: str = None):
        """
        Add additional variable and collect necessary raw data. 
        
        :param boundary: The boundary type for the variable. Should be either 'bg' or 'tract'.
        :type boundary: str
        :param year: The year for which the raw data is collected.
        :type year: int
        :param name: The name of the variable.
        :type name: str
        :param num: The list of numerator variables used to calculate the variable.
        :type num: list
        :param den: The list of denominator variables used to calculate the variable. Default is [1].
        :type den: list, optional
        :param description: Optional description of the variable. Default is None.
        :type description: str, optional
        
        :raises ValueError: If the variable name already exists.
        :raises ValueError: If the boundary type is invalid or the year is not between 2013 and 2022.
        :raises FileNotFoundError: If the raw data file doesn't exist. Run the census_data method first.
        
        :return: None
        :rtype: None
        """
        
        # Validate Variables
        self._validate_value(boundary, ['bg', 'tract'], 'boundary')
        self._validate_value(year, [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], 'year')
        
        # if name of variable already exists, raise error
        if name in self.all_vars_eqs:
            raise ValueError(f"Variable '{name}' already exists.")

        # open the raw data file as a df 
        if not os.path.exists(os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.gpkg")):
            raise FileNotFoundError(f"Raw data doesn't exist. Run census_data method first.")
        else:
            # Open the shapefile as a GeoDataFrame
            shapefile = gpd.read_file(os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.gpkg"))

        # add information to class instance 
        var_dict = {name:
                    {'num':num,
                    'den':den,
                    'description':description}}
        self.all_vars_eqs.update(var_dict)
        self.all_vars.append(name)

        # create list of raw data names that needs to be added
        vars = [var for var in num + den if isinstance(var, str)]
        missing_vars = [var for var in vars if var not in shapefile.keys()]
        if not missing_vars:
            pass
        else:
            # Pull Census data
            data_df = self._census_pull(self.geoids, boundary, missing_vars, self.api_key, year, pop_filter=self.low_pop_filter)
            # Fill missing columns
            data_df = self._fill_empty(data_df, boundary, self.geoids, self.api_key, year, verbose=False)  

            # create a new column with a shared 'key' to relate dataframes to
            if boundary == 'bg':
                shapefile['bg_fips'] = shapefile['GEOID']
                # merge geopandas shapefile with data_df shapefile
                data_df = data_df.merge(shapefile, on='bg_fips', how='right', suffixes=('', '_y'))
            elif boundary == 'tract':
                shapefile['tract_fips'] = shapefile['GEOID']
                # merge geopandas shapefile with data_df shapefile
                data_df = data_df.merge(shapefile, on='tract_fips', how='right', suffixes=('', '_y'))
            data_df.drop(data_df.filter(regex='_y$').columns, axis=1, inplace=True)

            # convert data_df to geopandas
            data_df = gpd.GeoDataFrame(data_df, geometry=data_df['geometry'])
            # reset index of geodataframe
            data_df['index'] = data_df['GEOID'].astype(np.int64)
            data_df = data_df.set_index('index')
            # Fill in missing holes
            data_df = self._fill_holes(data_df, boundary, self.geoids, self.api_key, year, interpolate=True, verbose=False)

            data_df.to_csv(os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.csv"))
            data_df.to_file(os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.gpkg"))


    # Method to create a configuration file before calculating SVI
    def configure_variables(self, config_file: str, exclude: list = None, include: list = None, inverse_vars: list = ['PERCAP', 'QRICH', 'MDHSEVAL']):
        """
        Configure variables and save them to a YAML file.

        :param config_file: The name of the configuration file.
        :type config_file: str
        :param exclude: Optional. A list of variable names to exclude for the configuration. Defaults to None.
        :type exclude: list, optional
        :param include: Optional. A list of variable names to only include for the configuration. Defaults to None.
        :type include: list, optional
        :param inverse_vars: Optional. A list of variable names to be inverted. Defaults to ['PERCAP', 'QRICH', 'MDHSEVAL'].
        :type inverse_vars: list, optional

        :returns: None
        :raises ValueError: If `exclude` and `include` arguments are both passed.
        :raises ValueError: If a variable in the `exclude` list is not available in `self.all_vars_eqs`.
        :raises ValueError: If a variable in the `include` list is not available in `self.all_vars_eqs`.
        """
        # raise error if exclude and include are both not none
        if (exclude is not None) and (include is not None):
            raise ValueError("Both exclude and include arguments cannot be passed.")

        output_dict = copy.deepcopy(self.all_vars_eqs)

        if exclude is not None:
            for key in exclude:
                self._validate_value(key, list(self.all_vars_eqs.keys()), key)
                del output_dict[key]
        
        if include is not None:
            for key in include:
                self._validate_value(key, list(self.all_vars_eqs.keys()), key)
            for key in list(output_dict.keys()):
                if key not in include:
                    del output_dict[key]


        with open(os.path.join(self.variables, f"{config_file}.yaml"), 'w') as file:
            yaml.dump(inverse_vars, file)
            file.write('---\n')
            yaml.dump(output_dict, file)

    
    # Method to calculate SVI -> input yaml file to determine what variables are included and how they are calculated  
    def calculate_svi(self, config_file: str, boundary: str = 'bg', year: int = 2019):
        """
        Calculate the Social Vulnerability Index (SVI) using two different methods.

        :param config_file: The name of the configuration file (without the extension) containing the SVI variables.
        :type config_file: str
        :param boundary: The boundary type for the SVI calculation. Default is 'bg'.
        :type boundary: str
        :param year: The year for which the SVI is calculated. Default is 2019.
        :type year: int

        :returns: None
        :raises ValueError: If the boundary type is invalid or the year is not between 2013 and 2022,

        This method reads a configuration file in YAML format, loads the raw data as a dataframe,
        calculates the SVI using two different methods, and saves the results to output files.

        **Method 1: Iterative Factor Analysis**
        
        - Conducts factor analysis on the input variables to identify significant components.
        - Scales the data and calculates initial loading factors.
        - Iteratively refactors the data based on the Kaiser Criterion until all significant variables are included.
        - Calculates the SVI using the scaled factors and the ratio of variance.
        - Appends the SVI variables to the output dataframe.

        **Method 2: Rank Method**

        - Ranks the input variables in descending order for each observation.
        - Calculates the sum of ranks for each observation.
        - Calculates the SVI using the rank sum.
        - Appends the SVI variables to the output dataframe.

        The output dataframe is saved as a GeoPackage file and a CSV file.
        Additionally, intermediate results from Method 1 such as significant components, loading factors, and variances
        are saved in an Excel file for documentation purposes.
        """
        # validate inputs
        self._validate_value(boundary, ['bg', 'tract'], 'boundary')
        self._validate_value(year, [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], 'year')

        # open the configuration file
        with open(os.path.join(self.variables, f"{config_file}.yaml")) as stream:
            try:
                docs = list(yaml.safe_load_all(stream))
            except yaml.YAMLError as exc:
                print(exc)

        # list of inverse varaibles
        yaml_list = docs[0]
        # dictionary of variables
        yaml_dict = docs[1]
        
        # load the raw data as a dataframe
        data_df = gpd.read_file(os.path.join(self.data,f"{self.project_name}_{year}_{boundary}_rawdata.gpkg"))
        data_df.set_index('index', inplace=True)
        output_df = data_df[['geometry']].copy()
        
        # calculate the variables
        for key, values in yaml_dict.items():
            # numerator
            num = data_df[values['num']].sum(axis=1)
            # denomenator
            if values['den'][0] == 1:
                den=1
            else:
                den = data_df[values['den']].sum(axis=1)
            # inverse and calculate
            if key in yaml_list:
                 output_df[key] = num/den*(-1)
            else:
                output_df[key] = num/den

        #  create copies for easier calculation of two different methods
        fa_df = output_df.drop(columns='geometry')
        rank_df = output_df.drop(columns='geometry')
           

        ################
        # SVI METHOD 1
        ################
        # calculate SVI method 1: Iterative Factor Analysis: FA_SVI_Unscaled, FA_SVI_Scaled, FA_SVI_Rank, FA_SVI_Percentile
        # TODO: set the following variables to self variable
        cumulative_var_min = 0.5
        sig_figs=1

        # labels
        var_labels = ['SS Loadings','Proportion Variance','Cumulative Variance']
        num_refactors=0
        df_variances=[]

        # PRIVATE METHODS
        def _calc_fa(n_factors, df):
            """Conduct Factor Analysis and compute Kaiser Criterion."""
            # Initalize FactorAnalyzer object
            fa = FactorAnalyzer(n_factors=n_factors, rotation='varimax',method='minres')
            # Conduct Factor Analysis fit
            fa.fit(df)
            # Calculate the eigenvalues
            eigenValue, value = fa.get_eigenvalues()
            df_eigen = pd.DataFrame({f'F{num_refactors}': range(1, len(eigenValue) + 1), 'Eigen value': eigenValue})
            # Kaiser Criterion, keep factors whose eigen value greater than 1
            kaiser_n = len(df_eigen[df_eigen['Eigen value'] >= 1])
            return fa, kaiser_n

        def _initalize_fa(fa_df):
            """Method to calculate factor analysis with max number of variables, re-calculate based on Kaiser Criterion, and calculate final loading variables"""
            # conduct initial factor analysis 
            fa, kaiser_n = _calc_fa(len(fa_df.columns), fa_df)
            # recompute factor analysis based on kaiser_n
            fa, kaiser_n = _calc_fa(kaiser_n, fa_df)
            # calculate loading factors
            facs = [f'F{num_refactors}: {(i + 1)}' for i in range(kaiser_n)]
            loading_factors = pd.DataFrame(data=fa.loadings_, index=fa_df.columns, columns=facs)
            return fa, kaiser_n, loading_factors, facs

        def _calc_variance(fa, n_factors, loading_factors, facs, df_variances):
            """Calculate the factor analysis variance statistics and determine significant components"""
            df_variance = pd.DataFrame(data=fa.get_factor_variance(), index=var_labels, columns=facs)
            ratioVariance = fa.get_factor_variance()[1] / fa.get_factor_variance()[1].sum()
            df_ratio_var = pd.DataFrame(data=ratioVariance.reshape((1, n_factors)), index=['Ratio Variance'], columns=facs)
            df_variance = pd.concat([df_variance, df_ratio_var],axis=0, join='outer')
            df_complete_variance = pd.concat([df_variance], axis=1)
            df_variances.append(df_variance)

            loading_factors_rounded = loading_factors.round(decimals=sig_figs)
            sig_components = []
            include = []
            for fac in facs:
                vars = loading_factors_rounded.loc[abs(loading_factors_rounded[fac]) >= cumulative_var_min].index.values
                sig_components.append([fac, vars])
                include.extend(list(set(vars) - set(include)))
            sig_components = pd.DataFrame(data=sig_components, columns=['Factor','Sig Components'])

            return sig_components, include, df_ratio_var, df_variances


        # 1. Scale data
        scaler = MinMaxScaler()
        fa_df = pd.DataFrame(data=scaler.fit_transform(fa_df), columns=fa_df.columns, index=fa_df.index)
        # 2. Conduct Factor Analysis and calculate initial loading factors
        fa, n_factors, loading_factors, facs = _initalize_fa(fa_df)
        # 3. Calculate initial variances
        sig_components, include, df_ratio_var, df_variances = _calc_variance(fa, n_factors, loading_factors, facs, df_variances)

        num_refactors+=1

        fa_refactor_df = fa_df[include].copy()
        # 4. Begin refactor loop with initial 'include' array
        while len(include) != len(fa_df.columns):
            fa_refactor_df = fa_df[include].copy()
            fa, n_factors, loading_factors, facs = _initalize_fa(fa_refactor_df)
            sig_components, include, df_ratio_var, df_variances = _calc_variance(fa, n_factors, loading_factors, facs, df_variances)

            # Determine if length of new dataset is equal to significant variables
            loading_factors_rounded = loading_factors.round(decimals=1)
            sig_components = []
            include = []
            for fac in facs:
                vars = loading_factors_rounded.loc[(loading_factors_rounded[fac] >= cumulative_var_min) | (
                    loading_factors_rounded[fac] <= -1*cumulative_var_min)].index.values
                sig_components.append([fac, vars])
                for var in vars:
                    # Need to also determine which factors should be added or subtracted
                    if var not in include:
                        include.append(var)

            sig_components = pd.DataFrame(data=sig_components, columns=['Factor', 'Sig Components'], index=facs)

            fa_df = fa_refactor_df.copy()
            num_refactors += 1
            
        # create list of excluded variables
        exclude = np.setdiff1d(np.array(output_df.columns), include).tolist()
        exclude.remove('geometry')

        # Compose the final index
        # In case of NaNs in fa_df, fill all with 0s, and create svi_dataframe
        fa_df.fillna(0, inplace=True)
        svi_factors = pd.DataFrame(data=fa.fit_transform(fa_df), index=fa_refactor_df.index, columns=facs)
        
        # Multiply by ratio of variance to scale
        dict_index = {}
        for i in range(n_factors):
            key = svi_factors.columns[i]
            value = svi_factors.iloc[:, i]*df_ratio_var.iloc[:, i].values
            dict_index.update({key: value})
        svi_index = pd.DataFrame(dict_index, index=fa_refactor_df.index, columns=facs)
        
        # Add SVI Variables to dataframe
        svi_index['FA_SVI_Unscaled'] = svi_index.sum(axis=1)
        svi_index['FA_SVI_Scaled'] = (svi_index['FA_SVI_Unscaled'] - svi_index['FA_SVI_Unscaled'].min()) / (svi_index['FA_SVI_Unscaled'].max() - svi_index['FA_SVI_Unscaled'].min())
        svi_index['FA_SVI_Rank'] = svi_index['FA_SVI_Scaled'].rank(ascending=False)
        svi_index['FA_SVI_Percentile'] = svi_index['FA_SVI_Rank'].rank(ascending=False, pct=True)
        # Append to output_df
        output_df = output_df.join(svi_index, on=output_df.index)
        
        # convert include and exclude lists into dataframe
        include_exclude = pd.DataFrame(data={'include': [[include]], 'exclude':[[exclude]]})
        
        # Create output excel sheet
        df_variances_c = pd.concat(df_variances, axis=1)
        with pd.ExcelWriter(os.path.join(self.documentation, f"{self.project_name}_{year}_{boundary}_{config_file}.xlsx")) as writer:
            # use the to_excel function and specify the sheet_name to store dataframes in single file
            sig_components.to_excel(writer, sheet_name='Significant Components')
            loading_factors.to_excel(writer, sheet_name='Loading Factors')
            df_variances_c.to_excel(writer, sheet_name='All Refactor Variances')
            df_variances[-1].to_excel(writer, sheet_name='Final Variances')
            include_exclude.to_excel(writer, sheet_name='Included and Excluded')



        ################
        # SVI METHOD 2
        ################

        # calculate SVI method 2: Rank Method: RM_SVI_Rank, RM_SVI_Percentile
        for col in rank_df.columns:
            rank_df[col] = rank_df[col].rank(ascending=False)
        rank_df['sum_rank'] = rank_df.sum(axis=1)
        output_df['RM_SVI_Rank'] = rank_df['sum_rank'].rank()
        output_df['RM_SVI_Percentile'] = rank_df['sum_rank'].rank(ascending=False, pct=True)
        

        # Order check
        # Determine if the slopes of the two ranks have opposite signs
        output_df = output_df.sort_values('FA_SVI_Rank')
        list1 = output_df['FA_SVI_Rank'].tolist()
        list2 = output_df['RM_SVI_Rank'].tolist()
        slope1, _ = np.polyfit(range(len(list1)), list1, 1)
        slope2, _ = np.polyfit(range(len(list2)), list2, 1)
        # Check if the slopes have different signs
        if np.sign(slope1) != np.sign(slope2):
            output_df['FA_SVI_Scaled'] = output_df['FA_SVI_Scaled'].max() - output_df['FA_SVI_Scaled']
            output_df['FA_SVI_Rank'] = output_df['FA_SVI_Rank'].max() - output_df['FA_SVI_Rank']
            output_df['FA_SVI_Percentile'] = output_df['FA_SVI_Percentile'].max() - output_df['FA_SVI_Percentile']
        else:
            pass

        # save geopackage and csv output
        output_df.to_file(os.path.join(self.svis, f"{self.project_name}_{year}_{boundary}_{config_file}_svi.gpkg"))
        output_df.to_csv(os.path.join(self.svis, f"{self.project_name}_{year}_{boundary}_{config_file}_svi.csv"))
         

    # Method to create various plots
    def plot_svi(self, plot_option: int, geopackages: list):
        """
        Simple plotting method to quickly map an SVI variable or compare two SVIs.

        :param plot_option: Which plot method to use: Either 1 (single SVI map), 2 (two side by side maps), or 3 (full comparison figure).
        :type plot_option: int
        :param geopackages: The required information for plotting, must be format: [year, boundary, config, variable]. Nested list if plot_option 2.
        :type geopackages: list


        :returns: matplotlib figure object
        :raises ValueError: If the boundary type is invalid or the year is not between 2013 and 2022,

        
        This method quickly creates an example SVI plot either by itself or in a comparative format. The plot options and their required information can be found below.

        **Plot Option 1: Single Plot**

        A single figure of a single SVI estimate. The geopackage parameter must be in the format [year, boundary, config, variable] where:

        - Year: SVI estimate year (int)
        - Boundary: Boundary of interest ('bg' or 'tract', str)
        - Config: Which config file was used to create the SVI estimate (str)
        - Variable: Which SVI variable to plot (i.e., the attributes of the SVI geopackages created, str). 

        **Plot Option 2: Simple Comparative Plot**

        A simple two by one figure to visually compare two differnet SVI estimates. These estimates can be from the same or different geopackages. The geopackages parameter should be a nested list of the same variables as described in plot option 1: [[year, boundary, config, variable],[year, boundary, config, variable]].

        **Plot Option 3: Complete Comparative Plot**

        A more detailed plotting option, that will produce a difference plot and calculate a linear regression. Because the difference map and linear regression require the same set of input geoids (i.e., the same locations in the geopackage), it is currently required that the variables come from the same geopackage, and its intended purpose is to therefore compare the differences between the Factor Analysis and Rank Method methodologies that have the same configuration. The geopackages input should be formated as follows: [year, boundary, config]. The additional plots show the following information:

        - Difference plot: Shows the The FA_SVI_Rank minus the RM_SVI_Rank to highlight areas where the factor analysis method is under (negative) and over (positive) predicting SVI rank when compared to the rank method. 
        - Linear Regression: Shows linear correlation betweeen factor analysis and rank method SVI estimates and automatically computes an r-squared value with p-value, 95% confidence interval, and 95% prediction interval.
        
        """
        # Special Use Boundaries Legened Element
        legend_elements = [Patch(facecolor='black', edgecolor='black',
                                label='No Data Available')]
        
        # Single geopackage plot
        if plot_option == 1:
            if len(geopackages) != 4:
                raise ValueError("geopackages must have length 4 for plot_option 1")
            fig, (ax1, ax2) = plt.subplots(2, 1, 
                            figsize=(6, 6), 
                            gridspec_kw={'height_ratios': [9, 1]})
            
            # extract variables
            year=geopackages[0]
            boundary=geopackages[1]
            config_file=geopackages[2]
            var = geopackages[3]

            # set titles
            ax1.set_title(f'{self.project_name}_{year}_{boundary}_{config_file}:\n{var}')
            ax1.legend(handles=legend_elements, loc='lower left')

            # read geopackage of data
            gdf=gpd.read_file(f"{self.svis}/{self.project_name}_{year}_{boundary}_{config_file}_svi.gpkg")
            # read geopackage of background
            background = gpd.read_file(f"{self.boundaries}/{self.project_name}_{year}_{boundary}.gpkg")

            # plot the figure
            self._plot_single(ax1, background, gdf, var)
            
            # plot cbar
            self._plot_cmap(fig,ax2,plot_option)
  
            
        # Double geopackage plot    
        elif plot_option == 2:
            if len(geopackages) != 2:
                raise ValueError("For plot option 2, geopackages must have exactly 2 elements.")
            for gp in geopackages:
                if len(gp) != 4:
                    raise ValueError("Each element in geopackages must have a length of 4.")
            # Create Figure
            fig, (ax1, ax2, ax3) = plt.subplots(1,3, 
                                    figsize=(12,6),
                                    gridspec_kw={'width_ratios':[9,1,9]})
            axes = [ax1, ax3]
            
            # shift center axis over, move y labels to right
            pos = ax2.get_position()
            pos.x0 -= 0.01875  
            pos.x1 -= 0.01875  
            ax2.set_position(pos)
            ax3.yaxis.tick_right()
            ax3.yaxis.set_label_position("right")
            
            for idx, geopackage in enumerate(geopackages):
                # extract variables
                year=geopackage[0]
                boundary=geopackage[1]
                config_file=geopackage[2]
                var = geopackage[3]

                #set titles
                axes[idx].set_title(f'{self.project_name}_{year}_{boundary}_{config_file}:\n{var}')
                axes[idx].legend(handles=legend_elements, loc='lower left')

                # read geopackage of data
                gdf=gpd.read_file(f"{self.svis}/{self.project_name}_{year}_{boundary}_{config_file}_svi.gpkg")
                # read geopackage of background
                background = gpd.read_file(f"{self.boundaries}/{self.project_name}_{year}_{boundary}.gpkg")
            
                # plot the figure
                self._plot_single(axes[idx], background, gdf, var)
                
            # plot cbar
            self._plot_cmap(fig,ax2,plot_option)
            
                   
        elif plot_option == 3:
            if len(geopackages) != 3:
                raise ValueError("For plot option 3, geopackages must have exactly 3 elements.")
           # Create Figure
            fig, axes = plt.subplots(2,3, 
                                    figsize=(10,8),
                                    gridspec_kw={'width_ratios':[9,1,9]})
            ax1, ax2, ax3, ax4, ax5, ax6 = axes.flatten()

            # shift center axis over, move y labels to right
            pos = ax2.get_position()
            pos.x0 -= 0.03
            pos.x1 -= 0.03  
            ax2.set_position(pos)
            ax3.yaxis.tick_right()
            ax3.yaxis.set_label_position("right")

            pos = ax5.get_position()
            pos.x0 -= 0.03  
            pos.x1 -= 0.03 
            ax5.set_position(pos)
            ax6.yaxis.tick_right()
            ax6.yaxis.set_label_position("right")
            
            axes = [ax1, ax3]

            gdfs = []
            vars=[]
            f_names=[]

            variables = ['FA_SVI_Rank', 'RM_SVI_Rank']
            for idx, var in enumerate(variables):
                # extract variables
                year=geopackages[0]
                boundary=geopackages[1]
                config_file=geopackages[2]

                #set titles
                axes[idx].set_title(f'{self.project_name}_{year}_{boundary}_{config_file}:\n{var}')
                axes[idx].legend(handles=legend_elements, loc='lower left')

                # read geopackage of data
                gdf=gpd.read_file(f"{self.svis}/{self.project_name}_{year}_{boundary}_{config_file}_svi.gpkg")
                # read geopackage of background
                background = gpd.read_file(f"{self.boundaries}/{self.project_name}_{year}_{boundary}.gpkg")
                gdfs.append(gdf)
                vars.append(var)
                f_names.append(f'{self.project_name}_{year}_{boundary}_{config_file}')
                # plot the figure
                self._plot_single(axes[idx], background, gdf, var)
                
            # plot cbar for SVI
            self._plot_cmap(fig,ax2,plot_option)

            # merge to remove any different locations
            merged_gdf = gdfs[0].merge(gdfs[1], left_index=True, right_index=True,suffixes=('_left', '_right'))
            # Create difference
            merged_gdf['difference'] = merged_gdf[f"{vars[0]}_left"] - merged_gdf[f"{vars[1]}_right"]

            # # Custom color ramp for map of differences
            cmap = mpl.cm.Spectral_r
            bounds = np.linspace(0, 1, 10+1)
            np.delete(bounds, 0)
            bins = []
            for bound in bounds:
                bins.append(merged_gdf['difference'].quantile(bound))
            norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

            # # plot difference
            ax4.set_title('Difference (L - R)')
            merged_gdf = gpd.GeoDataFrame(merged_gdf, geometry='geometry_left')
            self._plot_single(ax4, background, merged_gdf, 'difference', cmap='Spectral_r')
            ax4.legend(handles=legend_elements, loc='lower left')

            cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                                cax=ax5, orientation='vertical',
                                label="Under/Over Prediction")
            yticklabels = [str(round(float(label), 2)) for label in bins]
            cbar.ax.set_yticklabels(yticklabels)


            # determine correlation
            pearson_r, p_value = pearsonr(merged_gdf[f"{vars[0]}_left"], merged_gdf[f"{vars[1]}_right"])

            # calculate regression
            x = merged_gdf[f"{vars[0]}_left"].values
            y = merged_gdf[f"{vars[1]}_right"].values

            slope, intercept = np.polyfit(x, y, 1)  # linear model adjustment

            y_model = np.polyval([slope, intercept], x)   # modeling...

            x_mean = np.mean(x)
            y_mean = np.mean(y)
            n = x.size                        # number of samples
            m = 2                             # number of parameters
            dof = n - m                       # degrees of freedom
            t = stats.t.ppf(0.975, dof)       # Students statistic of interval confidence
            residual = y - y_model
            std_error = (np.sum(residual**2) / dof)**.5   # Standard deviation of the error

            # calculating the r2
            numerator = np.sum((x - x_mean)*(y - y_mean))
            denominator = (np.sum((x - x_mean)**2) * np.sum((y - y_mean)**2))**.5
            correlation_coef = numerator / denominator
            r2 = correlation_coef**2

            # mean squared error
            MSE = 1/n * np.sum((y - y_model)**2)

            # to plot the adjusted model
            x_line = np.linspace(np.min(x), np.max(x), 100)
            y_line = np.polyval([slope, intercept], x_line)

            # confidence interval
            ci = t * std_error * (1/n + (x_line - x_mean)**2 / np.sum((x - x_mean)**2))**.5
            # predicting interval
            pi = t * std_error * (1 + 1/n + (x_line - x_mean) **2 / np.sum((x - x_mean)**2))**.5

            # plot scatter points
            ax6.plot(x, y, 'o', color='royalblue')
            # plot regression line
            ax6.plot(x_line, y_line, color='royalblue')
            # prediction interval
            ax6.fill_between(x_line, 
                            y_line + pi, 
                            y_line - pi,
                            color='lightcyan', 
                            label='95% prediction interval')
            # confidence interval
            ax6.fill_between(x_line, 
                            y_line + ci, 
                            y_line - ci,
                            color='skyblue', 
                            label='95% confidence interval')
                # set axis labels and limits
            ax6.set_xlabel('Left plot')
            ax6.set_ylabel('Right plot')
            ax6.set_xlim([0, max(x)])
            ax6.set_ylim([0, max(y)])

            # rounding round appropriate values
            a = str(np.round(intercept))
            b = str(np.round(slope, 2))
            r2s = str(np.round(r2, 2))
            # p = str(np.round(p_value,2))
            MSEs = str(np.round(MSE))

            # plot text
            textstr = '\n'.join((f'y = {a} + {b}x',
                                f'$r^2$ = {r2s}',
                                f'p-value = {p_value:.03g}'))
            # patch properties
            props = dict(boxstyle='square', facecolor='lightgray', alpha=0.80)
            # text box in upper left in axes coords
            ax6.text(0.025, 0.975,
                    textstr,
                    transform=ax6.transAxes,
                    fontsize=8,
                    verticalalignment='top',
                    bbox=props)
            legend = ax6.legend(fontsize=8, loc=4, facecolor='lightgray')
            legend.get_frame().set_alpha(0.90)
            legend.get_frame().set_edgecolor("black")

        return fig



    ###################################################
    # PRIVATE METHODS (helper functions)
    ###################################################

    # Pull Census data
    def _census_pull(self, geoids, boundary, vars, api_key, year, pop_filter=None):
        """
        Given geoids, boundary, list of variables, api_key, and year, pull Census data.

        Parameters:
        geoids (list): A list of geoids.
        boundary (str): The type of boundary to fetch data for. Possible values are 'bg' or 'tract'.
        vars (list): A list of variables to fetch from the Census API.
        api_key (str): The API key for accessing the Census API.
        year (int): The year for which to fetch the data.
        pop_filter (int, optional): A population filter to remove boundaries with a population below a certain threshold. Defaults to None.

        Returns:
        pandas.DataFrame: A pandas DataFrame containing the fetched Census data.

        """
        c = Census(api_key)
        data=[]

        def fetch_data(var, state, county):
            if boundary == 'bg':
                data_pre = c.acs5.state_county_blockgroup(var, state, county, Census.ALL, year=year)
            elif boundary == 'tract':
                data_pre = c.acs5.state_county_tract(var, state, county, Census.ALL, year=year)
            else:
                data_pre = c.acs5.state_county(var, state, county, year=year)
            return data_pre
        
           # TODO: Add retry attempt
            # import time
            # for i in range(5):
            #     try:
            #         data_pre = c.acs5.state_county_blockgroup(var, state, county, Census.ALL, year=year)
            #         break
            #     except Exception as e:
            #         print(f"Attempt {i+1} failed with error: {e}")
            #         if i < 4:  # Don't sleep after the last attempt
            #             time.sleep(5)

        
        for geoid in geoids:
            if len(geoid) == 2:
                county = Census.ALL
                state = geoid
            else:
                # county = int(geoid[2:])
                # state = int(geoid[:2])
                county = geoid[2:]
                state = geoid[:2]

            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(fetch_data, var, state, county) for var in vars}
                for future in concurrent.futures.as_completed(futures):
                    data.extend(future.result()) 

        # convert data to pandas dataframe
        data_df = pd.DataFrame.from_dict(data)
        
        # create index column and other relevant fips columns
        if boundary == 'bg':
            data_df['index'] = data_df['state'] + data_df['county'] + data_df['tract'] + data_df['block group']
            data_df['bg_fips'] = data_df['state'] + data_df['county'] + data_df['tract'] + data_df['block group']
            data_df['tract_fips'] = data_df['state'] + data_df['county'] + data_df['tract']
            data_df['county_fips'] = data_df['state'] + data_df['county']
        elif boundary == 'tract':
            data_df['index'] = data_df['state'] + data_df['county'] + data_df['tract']
            data_df['tract_fips'] = data_df['state'] + data_df['county'] + data_df['tract']
            data_df['county_fips'] = data_df['state'] + data_df['county']
        else:
            data_df['index'] = data_df['state'] + data_df['county']
            data_df['county_fips'] = data_df['state'] + data_df['county']
        data_df = data_df.set_index('index')
        # Group to remove all of the zeros
        data_df = data_df.groupby(level=0).first()

        if pop_filter is not None:
            # filter out special use and low population boundaries
            # Special use BGs with extremely low household size such as airports, bases, prisons, etc.
            special_use = data_df.loc[data_df[['B25010_001E'][0]] < 0.01]
            data_df = data_df.drop(special_use.index)

            # Remove any boundary with less than X amount of people people
            low_pop = data_df.loc[data_df[['B01001_001E'][0]] <= pop_filter]
            data_df=data_df.drop(low_pop.index)

        return(data_df)

    # Fill missing columns Census data 
    def _fill_empty(self, data_df, boundary, geoids, api_key, year, verbose):
        """
        Finds and fills empty columns in the given DataFrame with the next highest available boundary data obtained from the Census API.

        Args:
            data_df (pandas.DataFrame): The DataFrame containing the data to be filled.
            boundary (str): The boundary type for the data (e.g., 'bg', 'tract').
            geoids (list): The list of geographic identifiers.
            api_key (str): The API key for accessing the Census API.
            year (int): The year for which the data is being filled.
            verbose (bool): If True, outputs a CSV file with information about the empty columns.

        Returns:
            pandas.DataFrame: The DataFrame with the empty columns filled.

        """
        # create output data file to save which columns are empty
        empty_output=[]

        empty_cols=[]
        for col in list(data_df):
            if data_df[col].isnull().sum() == len(data_df.index):  # if the # of nans is number of rows
                empty_cols.append(col)

        if empty_cols:
            # Get unique empty col types
            unique_empty = list(set([x[:6] for x in empty_cols]))
            for col in unique_empty:
                empty_output.append([col, f'{boundary} empty'])
                empty_output_name = os.path.join(self.data,f"{self.project_name}_{year}_{boundary}_missing_columns.csv")

            if boundary == 'bg':
                boundary = 'tract'
            else:
                boundary = 'county'
            fill_data = self._census_pull(geoids, boundary, empty_cols, api_key, year)
            fill_data_df = pd.DataFrame.from_dict(fill_data)
            # create reference columns
            fill_data_df['tract_fips'] = fill_data_df['state'] + fill_data_df['county'] + fill_data_df['tract']
            fill_data_df['county_fips'] = fill_data_df['state'] + fill_data_df['county']
            if boundary == 'tract':
                data_df = data_df.reset_index().merge(fill_data_df, 
                                                    on='tract_fips', 
                                                    suffixes=('', '_y')).set_index('index')
            else:
                data_df = data_df.reset_index().merge(fill_data_df, 
                                                    on='county_fips', 
                                                    suffixes=('', '_y')).set_index('index')
            for miss_col in empty_cols:
                new_col = miss_col + '_y'
                data_df[miss_col] = data_df[new_col]
                data_df = data_df.drop([new_col], axis=1)
            cols_to_drop = data_df.filter(like='_y', axis=1).columns
            data_df = data_df.drop(cols_to_drop, axis=1)

        if verbose is True and empty_cols:
             with open(empty_output_name, 'w', newline='') as file:
                writer = csv.writer(file)
                # Write rows to the CSV file
                writer.writerows(empty_output)

        return data_df
    
    # helper function, interpolate function
    def __interpolate(self, fips, var, neighbors, holes_df, data_df, filter_like, drop, low_range, high_range, interpolated_output):
        """
        Interpolates missing data for a specific variable using neighboring data.

        Args:
            fips (str): The FIPS code of the location.
            var (str): The variable to interpolate.
            neighbors (list): A list of FIPS codes of neighboring locations.
            holes_df (pandas.DataFrame): The DataFrame containing the missing data.
            data_df (pandas.DataFrame): The DataFrame containing the complete data.
            filter_like (str): A string to filter the columns of holes_df.
            drop (str): The column to drop from sum_neighbor_data.
            low_range (list): A list of low range values for calculating the median.
            high_range (list): A list of high range values for calculating the median.
            interpolated_output (list): A list to store information about interpolated data.

        Returns:
            pandas.DataFrame: The updated data_df with interpolated values.

        """
        # Select rows we are interested in 
        neighbor_data = holes_df.filter(items=neighbors, axis=0)
        # select columns we are interested in 
        neighbor_data = neighbor_data.filter(like=filter_like, axis=1)
        
        # order from decreasing to increasing
        # Extract the numeric part of the column names and convert to int
        def extract_number(col_name):
            return int(col_name.split('_')[1][:-1])
        # Sort the columns based on the numeric part
        sorted_columns = sorted(neighbor_data.columns, key=extract_number)
        # Reorder the DataFrame
        neighbor_data = neighbor_data[sorted_columns]

        # sum data
        sum_neighbor_data = neighbor_data.sum()
        # determine total number of sample points
        N = sum_neighbor_data[drop]
        
        # can now drop this value from dataframe
        sum_neighbor_data.drop(drop, inplace=True)
        
        if var == 'B01002_001E':
            # have to combine like female and male categories
            pairs = [['B01001_003E', 'B01001_027E'], ['B01001_004E', 'B01001_028E'], ['B01001_005E', 'B01001_029E'], 
                     ['B01001_006E', 'B01001_030E'], ['B01001_007E', 'B01001_031E'], ['B01001_008E', 'B01001_032E'], 
                     ['B01001_009E', 'B01001_033E'], ['B01001_010E', 'B01001_034E'], ['B01001_011E', 'B01001_035E'],
                     ['B01001_012E', 'B01001_036E'], ['B01001_013E', 'B01001_037E'], ['B01001_014E', 'B01001_038E'], 
                     ['B01001_015E', 'B01001_039E'], ['B01001_016E', 'B01001_040E'], ['B01001_017E', 'B01001_041E'],
                     ['B01001_018E', 'B01001_042E'], ['B01001_019E', 'B01001_043E'], ['B01001_020E', 'B01001_044E'],
                     ['B01001_021E', 'B01001_045E'], ['B01001_022E', 'B01001_046E'], ['B01001_023E', 'B01001_047E'],
                     ['B01001_024E', 'B01001_048E'], ['B01001_025E', 'B01001_049E']]

            col_names=['under 5','5 to 9','10 to 14','15 to 17','18 to 19','20','21','22 to 24','25 to 29',
                        '30 to 34','35 to 39','40 to 44','45 to 49','50 to 54','55 to 59','60 to 61','62 to 64',
                        '65 to 66','67 to 69','70 to 74','75 to 79','80 to 84','over 85']
            for idx, pair in enumerate(pairs):
                sum_neighbor_data[col_names[idx]] = sum_neighbor_data[pair].sum()
                for item in pair:
                    sum_neighbor_data.drop(item, inplace=True)


        if N > self.min_iterp_neighbors:
            # convert to list
            sum_neighbor_data = sum_neighbor_data.tolist()
            # create cumulative sum percentage list
            cumsum_perc = []
            j = 0
            for i in range(0, len(sum_neighbor_data)):
                j += sum_neighbor_data[i]/N
                cumsum_perc.append(j)

            # NOTE: Important: high_range max value is only +1 the low value - recommended practice by Census
            # create median calculation dictionary
            calc = pd.DataFrame.from_dict({'low_range':low_range,
                                            'high_range':high_range,
                                            'freq': sum_neighbor_data,
                                            'cumsum_perc': cumsum_perc})

            # determine lower limit of the median interval
            index = (calc['freq'].cumsum() >= N/2).idxmax()
            #L1 = calc['low_range'][index+1]
            

            if index == 0:
                # not enough info, median is in lowest bound, don't interpolate
                pass
            else:
                # determine median count 
                median_count = np.round(N/2,0)
                # Determine number of points in range needed to get to median
                points_needed =  median_count - calc['freq'].cumsum()[index-1]

                # determine proportion (returns 0 if divide by 0)
                p = np.divide(points_needed, calc['freq'][index], out=np.zeros_like(points_needed), where=calc['freq'].cumsum()[index]!=0)
               
                # # determine the width of the median interval
                width = calc['high_range'][index] - calc['low_range'][index]
                
                # calculate the new value 
                interpolated_value = p*width+calc['low_range'][index]

                # fill in values of data frame
                data_df.loc[fips, var] = interpolated_value
                    
                interpolated_output.append([f'{fips}', var, 'Interpolated'])


                # # determine the number of data points below the median interval
                # cumsum_before = calc['freq'].cumsum()[index-1]
                # # determine the width of the median interval
                # width = calc['high_range'][index + 1] - calc['low_range'][index + 1] + 1
                # # determine the number of data points in the median interval
                # freq_medain = calc['freq'][index + 1]
                # # rare case if new median falls in range of values with zero frequency
                # if freq_medain == 0:
                #     median = L1 + (N/2 - cumsum_before)
                # else:
                #     # calculate median
                #     median = L1 + (N/2 - cumsum_before) / freq_medain * width
                # print(L1, N, cumsum_before, freq_medain, width, median)
                # # fill in values of data frame
                # data_df.loc[fips, var] = median
                # interpolated_output.append([f'{fips}', var, 'Interpolated'])


        return data_df
  
    # helper function, find holes
    def __find_holes(self, data_df):
        """
        Finds missing holes in the given data DataFrame.

        Args:
            data_df (DataFrame): The input DataFrame to search for missing holes.

        Returns:
            tuple: A tuple containing two lists - `miss_vals` and `unique_missing_vals`.
                - `miss_vals` (list): A list of missing values in the DataFrame. First value is GEOID of hole, and second value is variable.
                - `unique_missing_vals` (list): A list of unique missing values found in the DataFrame.

        """
        # Fill in missing holes
        miss_vals = data_df.where(data_df.map(lambda x: isinstance(x, (np.int64, float)) and x < 0)).stack().index
        # Find the unique missing_vars
        unique_missing_vals = []
        for miss_val in miss_vals:
            if miss_val[1] not in unique_missing_vals:
                unique_missing_vals.append(miss_val[1])  

        return miss_vals, unique_missing_vals
    
    # helper function, fill holes without Interpolate
    def __fil_holes_wo_interopolate(self, data_df, miss_vals, unique_missing_vals, boundary, geoids, api_key, year, interpolated_output):
        """
        Fill missing values in the data dataframe without interpolation.

        Args:
            data_df (pandas.DataFrame): The dataframe containing the data.
            miss_vals (list): A nested list of missing values in the DataFrame. First value is GEOID of hole, and second value is variable.
            unique_missing_vals (list): A list of unique missing values.
            boundary (str): The boundary type ('bg' for tract boundary, 'county' for county boundary).
            geoids (list): A list of geoids.
            api_key (str): The API key for accessing census data.
            year (int): The year of the census data.
            interpolated_output (list): A list to store information about interpolated data.

        Returns:
            pandas.DataFrame: The dataframe with missing values filled.

        """
        if boundary == 'bg':
            tract_fill_df = self._census_pull(geoids, 'tract', unique_missing_vals, api_key, year)
            county_fill_df = self._census_pull(geoids, 'county', unique_missing_vals, api_key, year)
            for miss_val in miss_vals:
                fips = miss_val[0] 
                var = miss_val[1]
                tract_fips = data_df.loc[fips, "tract_fips"]
                county_fips = data_df.loc[fips, "county_fips"]
                if tract_fill_df.loc[tract_fips, var] < -1:
                    data_df.loc[fips, var] = county_fill_df.loc[county_fips, var]
                    interpolated_output.append([f'{fips}', var, 'County Filled'])
                else:
                    data_df.loc[fips, var] = tract_fill_df.loc[tract_fips, var]
                    interpolated_output.append([f'{fips}', var, 'Tract Filled'])

        else:
            county_fill_df = self._census_pull(geoids, 'county', unique_missing_vals, api_key, year)
            for miss_val in miss_vals:
                fips = miss_val[0] 
                var = miss_val[1]
                county_fips = data_df.loc[fips, "county_fips"]
                data_df.loc[fips, var] = county_fill_df.loc[county_fips, var]
                interpolated_output.append([f'{fips}', var, 'County Filled'])

        return data_df

    # helper function, fill holes with interpolate
    def __fil_holes_w_interpolate(self, data_df, miss_vals, unique_missing_vals, boundary, geoids, api_key, year, interpolated_output):
        """
        Interpolates missing values in the data dataframe using neighboring values.

        Parameters:
        - data_df (DataFrame): The dataframe containing the data with missing values.
        - miss_vals (list): A nestedlist of missing values in the DataFrame. First value is GEOID of hole, and second value is variable.
        - unique_missing_vals (list): A list of unique missing values.
        - boundary (str): The boundary type for the census data.
        - geoids (list): A list of FIPS codes.
        - api_key (str): The API key for accessing the census data.
        - year (str): The year of the census data.
        - interpolated_output (str): A list to store information about interpolated data.

        Returns:
        - data_df (DataFrame): The dataframe with interpolated values.
        """
        
        # pull variables for data that can be interpolated
        # Currently, the following variables can be interpolated:
            # B25064, MDGRENT
            # B25077, MDHSEVAL
            # B01002, MEDAGE

        variables = ['B25075_001E', 'B25075_002E', 'B25075_003E', 'B25075_004E',
                    'B25075_005E', 'B25075_006E', 'B25075_007E', 'B25075_008E',
                    'B25075_009E', 'B25075_010E', 'B25075_011E', 'B25075_012E',
                    'B25075_013E', 'B25075_014E', 'B25075_015E', 'B25075_016E',
                    'B25075_017E', 'B25075_018E', 'B25075_019E', 'B25075_020E',
                    'B25075_021E', 'B25075_022E', 'B25075_023E', 'B25075_024E',
                    'B25075_025E', 'B25075_026E', 'B25075_027E', 'B25063_002E', 
                    'B25063_003E', 'B25063_004E', 'B25063_005E', 'B25063_006E', 
                    'B25063_007E', 'B25063_008E', 'B25063_009E', 'B25063_010E', 
                    'B25063_011E', 'B25063_012E', 'B25063_013E', 'B25063_014E', 
                    'B25063_015E', 'B25063_016E', 'B25063_017E', 'B25063_018E', 
                    'B25063_019E', 'B25063_020E', 'B25063_021E', 'B25063_022E', 
                    'B25063_023E', 'B25063_024E', 'B25063_025E', 'B25063_026E', 
                    'B01001_001E', 'B01001_003E', 'B01001_004E', 'B01001_005E', 
                    'B01001_006E', 'B01001_007E', 'B01001_008E', 'B01001_009E', 
                    'B01001_010E', 'B01001_011E', 'B01001_012E', 'B01001_013E', 
                    'B01001_014E', 'B01001_015E', 'B01001_016E', 'B01001_017E', 
                    'B01001_018E', 'B01001_019E', 'B01001_020E', 'B01001_021E', 
                    'B01001_022E', 'B01001_023E', 'B01001_024E', 'B01001_025E', 
                    'B01001_027E', 'B01001_028E', 'B01001_029E', 'B01001_030E', 
                    'B01001_031E', 'B01001_032E', 'B01001_033E', 'B01001_034E', 
                    'B01001_035E', 'B01001_036E', 'B01001_037E', 'B01001_038E', 
                    'B01001_039E', 'B01001_040E', 'B01001_041E', 'B01001_042E', 
                    'B01001_043E', 'B01001_044E', 'B01001_045E', 'B01001_046E', 
                    'B01001_047E', 'B01001_048E', 'B01001_049E']

        # pull data to interpolate holes
        holes_df = self._census_pull(geoids, boundary, variables, api_key, year)

        for miss_val in miss_vals:
            fips = miss_val[0] 
            var = miss_val[1]
            # determine neighbors
            neighbors = data_df[~data_df.geometry.disjoint(data_df.loc[fips].geometry)].index.tolist()
            neighbors = [str(x) for x in neighbors]

            if var == 'B25064_001E':
                # GROSS RENT
                # variable name: MDGRENT
                # filter value like: B25063
                # value to drop: B25063_002E
                # low range values: [0,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,900,1000,1250,1500,2000,2500,3000,3500]
                # high range values: [99,149,199,249,299,349,399,449,499,549,599,649,699,749,799,899,999,1249,1499,1999,2499,2999,3499,3501]

                data_df = self.__interpolate(fips,
                                             var,
                                             neighbors,
                                             holes_df,
                                             data_df, 
                                             'B25063', 
                                             'B25063_002E', 
                                             [0,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,900,1000,1250,1500,2000,2500,3000,3500], 
                                             [99,149,199,249,299,349,399,449,499,549,599,649,699,749,799,899,999,1249,1499,1999,2499,2999,3499,3501],
                                             interpolated_output)
                
                
            elif var == 'B25077_001E':
                # Housing Value
                # variable name: MDHSEVAL
                # filter value like: B25075
                # value to drop: B25075_001E
                # low range: [0, 10000, 15000, 20000, 25000, 30000,35000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000,  175000, 200000, 250000, 300000, 400000, 500000, 750000, 1000000, 1500000, 2000000],
                # high_range: [9999,14999,19999,24999,29999,34999,39999,49999,59999,69999,79999, 89999,99999,124999,149999,174999, 199999,249999,299999,399999,499999,749999,999999,1499999,1999999,2000001]

                data_df = self.__interpolate(fips,
                                             var,
                                             neighbors,
                                             holes_df,
                                             data_df, 
                                             'B25075', 
                                             'B25075_001E', 
                                            [0, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000,  175000, 200000, 250000, 300000, 400000, 500000, 750000, 1000000, 1500000, 2000000], 
                                             [9999,14999,19999,24999,29999,34999,39999,49999,59999,69999,79999, 89999,99999,124999,149999,174999, 199999,249999,299999,399999,499999,749999,999999,1499999,1999999,2000001],
                                             interpolated_output)

            elif var == 'B01002_001E':
                # Median Age
                # variable name: MEDAGE
                # filter value like: B01001
                # value to drop: B01001_001E
                # low range: [0, 5, 10, 15, 18, 20, 21, 22, 25, 30, 35, 40, 45, 50, 55, 60, 62, 65, 67, 70, 75,80, 85]
                # high_range: [4, 9, 14, 17, 19, 20, 21, 24, 29, 34, 39, 44, 49, 54, 59, 61, 64, 66, 69, 74, 79, 84, 86]

                data_df = self.__interpolate(fips,
                                             var,
                                             neighbors,
                                             holes_df,
                                             data_df, 
                                             'B01001', 
                                             'B01001_001E', 
                                            [0, 5, 10, 15, 18, 20, 21, 22, 25, 30, 35, 40, 45, 50, 55, 60, 62, 65, 67, 70, 75,80, 85],
                                             [4, 9, 14, 17, 19, 20, 21, 24, 29, 34, 39, 44, 49, 54, 59, 61, 64, 66, 69, 74, 79, 84, 86],
                                             interpolated_output)




        # recalculate all negatives in dataframe after all variables calculated 
        # fill wo interpolate these holes to reduce number of census api calls 
        # should cut down on time 


        
        return data_df
    
    # Fill missing holes in Census data
    def _fill_holes(self, data_df, boundary, geoids, api_key, year, interpolate, verbose=False):
        """
        Fill missing values in the given DataFrame by interpolating or without interpolating.

        Args:
            data_df (pandas.DataFrame): The DataFrame containing the data with missing values.
            boundary (str): The boundary value.
            geoids (list): The list of geoids.
            api_key (str): The API key for accessing the data.
            year (int): The year of the data.
            interpolate (bool): If True, interpolate missing values. If False, fill missing values without interpolation.
            verbose (bool, optional): If True, save the interpolated info output as a CSV file. Defaults to False.

        Returns:
            pandas.DataFrame: The DataFrame with missing values filled.

        """
        if year <= 2014:
            interpolate = False
        # create output data file to save interpolated results
        interpolated_output=[]

        # find holes
        miss_vals, unique_missing_vals = self.__find_holes(data_df)       

        if interpolate is True:
            data_df = self.__fil_holes_w_interpolate(data_df, miss_vals, unique_missing_vals, boundary, geoids, api_key, year, interpolated_output)
            # find remaining holes and fill if there are any
            miss_vals, unique_missing_vals = self.__find_holes(data_df)
            if not miss_vals.empty:
                data_df = self.__fil_holes_wo_interopolate(data_df, miss_vals, unique_missing_vals, boundary, geoids, api_key, year, interpolated_output)

        else:
            data_df = self.__fil_holes_wo_interopolate(data_df, miss_vals, unique_missing_vals, boundary, geoids, api_key, year, interpolated_output)
               
        if verbose is True:
            # save the interpolated_output as a csv 
            with open(os.path.join(self.data,f"{self.project_name}_{year}_{boundary}_missing_values.csv"), 'w', newline='') as file:
                writer = csv.writer(file)
                # Write rows to the CSV file
                writer.writerows(interpolated_output)

            
        return data_df
    
    def _plot_single(self,ax,background,gdf, var, cmap=None):
        "Produce single SVI plot"
        # plot background
        background.plot(ax=ax, color='black')
        
        # Add gridlines
        ax.grid(True, which='major', color='grey', linewidth=0.25)

        if cmap is None:
            # select proper color ramp
            if gdf[var].max() > 1:
                cmap = 'coolwarm_r'
            else:
                cmap = 'coolwarm'

        else:
            cmap=cmap

        # plot the figure
        gdf.plot(ax=ax,
                    column=var,
                    cmap=cmap,
                    scheme='quantiles',
                    k=10,
                    edgecolor='black',
                    linewidth=0.5)
        
    def _plot_cmap(self, fig, ax, plot_option):
        """Plot SVI cmap"""
        cmap = mpl.cm.coolwarm
        bounds = np.linspace(0, 1, 10+1)
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        labels = ['0','10','20','30','40','50','60','70','80','90','100']
        if plot_option == 1:
            cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                            cax=ax, orientation='horizontal',
                            label="Percentile")
            cbar.ax.set_xticklabels(labels)
        else:
            cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                            cax=ax, orientation='vertical',
                            label="Percentile")
            cbar.ax.set_yticklabels(labels)




