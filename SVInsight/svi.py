
import os 
import csv
import copy
import shutil
import zipfile
import numpy as np
import pandas as pd
from ftplib import FTP
import geopandas as gpd
from census import Census
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from sklearn.preprocessing import MinMaxScaler
from factor_analyzer import FactorAnalyzer
import yaml

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
    def validate_value(value, valid_options, value_name):
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
    def validate_format(value, type, value_name):
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
    def geoid_format(geoids):
        """
        Validates the format of a list of GEOIDs.

        Args:
            geoids (list): A list of GEOIDs to be validated. Each GEOID must be length 2 or 5.

        Raises:
            ValueError: If the GEOIDs are not all of the same length, either 2 or 5.

        Returns:
            None
        """
        lengths = {len(geoid) for geoid in geoids}
        if len(lengths) > 1 or (list(lengths)[0] not in [2, 5]):
            raise ValueError("All GEOIDs must be of the same length, either 2 or 5.")
                

    def __init__(self, project_name: str, file_path: str, api_key: str, geoids: list[str]):
        """
        Initialize the SVInsight class.

        Parameters:
        - project_name (str): The name of the project. Will be used in file structure and names of saved files.
        - file_path (str): The file path where the project will be saved.
        - api_key (str): The Census API key for accessing data.
        - geoids (list[str]): A list of geographic identifiers. Must all be either length 2 or 5.
        

        Raises:
        - FileNotFoundError: If the file path does not exist.
        - ValueError: If the GEOIDs are not all of the same length, either 2 or 5.
        - TypeError: If a value is not of the expected type.


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
        self.validate_format(project_name, str, 'project_name')
        self.validate_format(file_path, str, 'file_path')
        self.validate_format(api_key, str, 'api_key')
        self.validate_format(geoids, list, 'geoids')
        self.geoid_format(geoids)

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
    def boundaries_data(self, boundary: str = 'bg', year: int = 2019) -> gpd.GeoDataFrame:
        """
        Pulls block group or tract data from the Census FTP site.

        Args:
            boundary (str): The type of boundary. Defaults to 'bg'. Acceptable values are 'bg', or 'tract'.
            year (str): The year of the data. Defaults to '2019'.

        Returns:
            gpd.GeoDataFrame: The boundary data as a GeoDataFrame.

        Raises:
            ValueError: If the boundary type is invalid, the year is not between 2010 and 2022, or geoids not properly formated.
        """
        
        # Validate Variables
        self.validate_value(boundary, ['bg', 'tract'], 'boundary')
        self.validate_value(year, [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], 'year')
        self.validate_format(boundary, str, 'boundary')
        self.validate_format(year, int, 'year')


        # If shapefile already exists, pass 
        if os.path.exists(os.path.join(self.boundaries, f"{self.project_name}_{year}_{boundary}.gpkg")):
            pass
        else:

            # create final output geodataframe
            output = gpd.GeoDataFrame()

            # helper functions
            def _download(year, state, boundary):
                """
                Downloads a shapefile from a remote FTP server, extracts it, and returns the boundary shapefile as a GeoDataFrame.

                Args:
                    year (int): The year of the shapefile.
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
                # Open the file locally and write it to folder
                with open(zipped_dir, "wb") as file:
                    ftp.retrbinary(f"RETR {zipped_filename}", file.write)

                # Unzip the file
                with zipfile.ZipFile(f"{zipped_dir}", 'r') as zip_ref:
                    zip_ref.extractall(filename_dir)

                # Read the shapefile with geopandas
                boundary_shp = gpd.read_file(f"{filename_dir}/{filename}.shp")


                # remove the zipped and unzipped files
                os.remove(zipped_dir)
                shutil.rmtree(filename_dir)

                return boundary_shp

            # initiate FTP
            ftp = FTP('ftp2.census.gov')
            ftp.login()
            ftp.cwd(f'geo/tiger/GENZ{year}/shp/')

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
            ftp.quit()

            return output
    

    # Method to pull census data and fill holes
    def census_data(self, boundary: str = 'bg', year: int = 2019, interpolate: bool = True, verbose: bool = False, overwrite: bool = False):
        '''
        Pulls Census data for a specific boundary and year.

        Parameters:
            boundary (str): The boundary type to retrieve data for. Valid options are 'bg' (block group) and 'tract' (census tract).
            year (int): The year of the Census data to retrieve. Valid options are from 2010 to 2022.
            interpolate (bool, optional): Whether to interpolate missing data. Defaults to True.
            verbose (bool, optional): Whether to display verbose output. Defaults to False.
            overwrite (bool, optional): Whether to overwrite existing data. Defaults to False.

        Raises:
            ValueError: If the boundary type is invalid or the year is not between 2010 and 2022.
            FileNotFoundError: If the shapefile for the specified boundary and year does not exist.

        Returns:
            None
        '''
        # Validate Variables
        self.validate_value(boundary, ['bg', 'tract'], 'boundary')
        self.validate_value(year, [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], 'year')
        self.validate_format(boundary, str, 'boundary')
        self.validate_format(year, int, 'year')

        # If data already exists and overwrite is False, don't pull data 
        if os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.gpkg") and overwrite is False:
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
            data_df['index'] = data_df['GEOID'].astype(int)
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

        Args:
            vars (list): Optional. List of variables to print descriptions for. If not provided, descriptions for all variables will be printed.

        Raises:
            ValueError: If any variable in `vars` is not an available variable.

        Returns:
            None
        """

        # Raise exception if var in vars not an available variable
        if vars is not None:
            for var in vars:
                self.validate_value(var, list(self.all_vars_eqs.keys()), var)

        if vars is None:
            vars = list(self.all_vars_eqs.keys())
        for var in vars:
            print(f"{var}: {self.all_vars_eqs[var]['description']}")
        

    # Method to add a variable
    def add_variable(self, boundary: str, year: int, name:str, num: list, den: list = [1], description: str = None):
        """
        Add additional variable and collect necessary raw data. 
        
        Args:
            boundary (str): The boundary type for the variable. Should be either 'bg' or 'tract'.
            year (int): The year for which the raw data is collected.
            name (str): The name of the variable.
            num (list): The list of numerator variables used to calculate the variable.
            den (list): The list of denominator variables used to calculate the variable. Default is [1].
            description (str): Optional description of the variable. Default is None.
        
        Raises:
            ValueError: If the variable name already exists.
             ValueError: If the boundary type is invalid or the year is not between 2010 and 2022.
            FileNotFoundError: If the raw data file doesn't exist. Run the census_data method first.
        
        Returns:
            None
        """
        
        # Validate Variables
        self.validate_value(boundary, ['bg', 'tract'], 'boundary')
        self.validate_value(year, [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], 'year')
        
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
            data_df = self._census_pull(self.geoids, boundary, missing_vars, self.api_key, year,pop_filter=None)
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
            data_df['index'] = data_df['GEOID'].astype(int)
            data_df = data_df.set_index('index')
            # Fill in missing holes
            data_df = self._fill_holes(data_df, boundary, self.geoids, self.api_key, year, interpolate=True, verbose=False)

            data_df.to_csv(os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.csv"))
            data_df.to_file(os.path.join(self.data, f"{self.project_name}_{year}_{boundary}_rawdata.gpkg"))


    # Method to create a configuration file before calculating SVI
    def configure_variables(self, config_file: str , exclude: list = None, include: list = None, inverse_vars = ['PERCAP' , 'QRICH', 'MDHSEVAL']):
        """
        Configure variables and save them to a YAML file. Can either exclude variables with exclude argument, or only include specific variables with include argument. 

        Args:
            config_name (str, optional): The name of the configuration file. 
            exclude (list, optional): A list of variable names to exclude for the configuration. Defaults to None.
            include (list, optional): A list of variable names to only include for the configuration. Defaults to None. 

        Returns:
            None

        Raises:
            ValueError: If `exclude` and `include` arguments are both passed.
            ValueError: If a variable in the `exclude` list is not available in `self.all_vars_eqs`.
            ValueError: If a variable in the `include` list is not available in `self.all_vars_eqs`.


        """
        # raise error if exclude and include are both not none
        if (exclude is not None) and (include is not None):
            raise ValueError("Both exclude and include arguments cannot be passed.")

        output_dict = copy.deepcopy(self.all_vars_eqs)

        if exclude is not None:
            for key in exclude:
                self.validate_value(key, list(self.all_vars_eqs.keys()), key)
                del output_dict[key]
        
        if include is not None:
            for key in include:
                self.validate_value(key, list(self.all_vars_eqs.keys()), key)
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

        Args:
            config_file (str): The name of the configuration file (without the extension) containing the SVI variables.
            boundary (str): The boundary type for the SVI calculation. Default is 'bg'.
            year (int): The year for which the SVI is calculated. Default is 2019.

        Returns:
            None
        
        Raises:
            ValueError: If the boundary type is invalid or the year is not between 2010 and 2022,

        This method reads a configuration file in YAML format, loads the raw data as a dataframe,
        calculates the SVI using two different methods, and saves the results to output files.

        Method 1: Iterative Factor Analysis
        - Conducts factor analysis on the input variables to identify significant components.
        - Scales the data and calculates initial loading factors.
        - Iteratively refactors the data based on the Kaiser Criterion until all significant variables are included.
        - Calculates the SVI using the scaled factors and the ratio of variance.
        - Appends the SVI variables to the output dataframe.

        Method 2: Rank Method
        - Ranks the input variables in descending order for each observation.
        - Calculates the sum of ranks for each observation.
        - Calculates the SVI using the rank sum.
        - Appends the SVI variables to the output dataframe.

        The output dataframe is saved as a GeoPackage file and a CSV file.
        Additionally, intermediate results from method 1 such as significant components, loading factors, and variances
        are saved in an Excel file for documentation purposes.
        """
        # validate inputs
        self.validate_value(boundary, ['bg', 'tract'], 'boundary')
        self.validate_value(year, [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], 'year')

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
        

        # save geopackage and csv output
        output_df.to_file(os.path.join(self.svis, f"{self.project_name}_{year}_{boundary}_{config_file}_svi.gpkg"))
        data_df.to_csv(os.path.join(self.svis, f"{self.project_name}_{year}_{boundary}_{config_file}_svi.csv"))
         




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
        
        for geoid in geoids:
            if len(geoid) == 2:
                county = Census.ALL
                state = geoid
            else:
                county = int(geoid[2:])
                state = int(geoid[:2])

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
            data_df['country_fips'] = data_df['state'] + data_df['county']
        elif boundary == 'tract':
            data_df['index'] = data_df['state'] + data_df['county'] + data_df['tract']
            data_df['tract_fips'] = data_df['state'] + data_df['county'] + data_df['tract']
            data_df['country_fips'] = data_df['state'] + data_df['county']
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

        if verbose is True:
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
        # Filter out the data that we want
        neighbor_data = holes_df.filter(items=neighbors, axis=0)
        neighbor_data = neighbor_data.filter(like=filter_like, axis=1)
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
            index = abs(calc['freq'].cumsum() - N/2).idxmin()
            L1 = calc['low_range'][index+1]

            if index == 0:
                # not enough info, don't interpolate
                pass
            else:
                # determine the number of data points below the median interval
                cumsum_before = calc['freq'].cumsum()[index-1]
                # determine the number of data points in the median interval
                freq_medain = calc['freq'][index + 1]
                # rare case if new median falls in range of values with zero frequency
                if freq_medain == 0:
                    freq_medain = 1
                # determine the width of the median interval
                width = calc['high_range'][index + 1] - calc['low_range'][index + 1] + 1
                # calculate median
                median = L1 + (N/2 - cumsum_before) / freq_medain * width
                # fill in values of data frame
                data_df.loc[fips, var] = median
                interpolated_output.append([f'{fips}', var, 'Interpolated'])


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
        miss_vals = data_df.where(data_df.map(lambda x: isinstance(x, (int, float)) and x < 0)).stack().index
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
                                            [0, 10000, 15000, 20000, 25000, 30000,35000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000,  175000, 200000, 250000, 300000, 400000, 500000, 750000, 1000000, 1500000, 2000000], 
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
    


# Initialize an instance of SVInsight
def project(project_name: str, file_path: str, api_key: str, geoids: list[str]):
    return SVInsight(project_name, file_path, api_key, geoids)