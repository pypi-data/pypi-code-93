import glob
import json
import os
import re
from os.path import sep
import geopandas as gpd

import pandas as pd
from zipfile import ZipFile
from fiona.errors import DriverError

from xander.connectors.oracle.database import Oracle
from xander.engine.xander import logger


def export_csv(output, path):
    """
    Exports the dataset in chucks. This allows a more efficient and fast export of the dataset.
    """

    n = 50000
    output = [output[i:i + n] for i in range(0, output.shape[0], n)]

    header = True
    for chunk in output:
        chunk.to_csv(path, header=header, mode='w' if header else 'a', sep=';', index=False)
        header = False

    return True


def define_output_names(outputs, destination_path, component_slug):
    """
    Analyze the output and generates a list of object to save paired with the file name.

    @param component_slug: slug of the component currently running
    @param destination_path: destination path for the output
    @param outputs: list of components output
    @return: list of outputs and list of outputs names
    """

    output_list = []
    tuple_case = False

    # Case 1: (string, obj)
    if isinstance(outputs, tuple) and len(outputs) == 2 and isinstance(outputs[0], str):
        output_list.append(outputs)
        tuple_case = True

    # Case 2: list of tuples -> [(string, obj)]
    elif isinstance(outputs, list) and len(outputs) > 0 and isinstance(outputs[0], tuple) and len(
            outputs[0]) == 2 and isinstance(outputs[0][0], str):
        output_list = outputs
        tuple_case = True

    # Case 3: list of objs -> [obj]
    elif isinstance(outputs, list) and len(outputs) > 0 and isinstance(outputs[0], object):
        output_list = outputs

    # Case 4: obj
    else:
        output_list.append(outputs)

    # Initialize the list of output names with a default name that is the name of the component followed by the index
    # of the parameters in the list. In this way the user can understand easily the content of the file.
    names = [os.path.join(destination_path, component_slug + f'_out{i}') for i in range(0, len(output_list))]

    output_list_cleaned = output_list

    # If we fall in the case of tuple or list of tuples we extract the filename from the first element of the tuple.
    if tuple_case:

        # Iterate over all outputs
        for i, output in enumerate(output_list):
            if len(output[0]) > 0:
                names[i] = os.path.join(destination_path, output[0])
                output_list_cleaned[i] = output[1]

    # Return the list of outputs and names
    return output_list_cleaned, names


def read_file(folder, filename, params=None, version=-1, max_version=-1):
    """
    Search in the folder the file and retrieve the specified version.
    """

    latest_version_filter = find_last_version(folder=folder, filename=filename, version=version,
                                              max_version=max_version)

    fixed_filename = filename

    if latest_version_filter is not None:
        fixed_filename = os.path.join(sep.join(filename.split(sep)[:-1]),
                                      filename.split(sep)[-1].split('.')[0] + '_v{}.'.format(
                                          latest_version_filter) + filename.split(sep)[-1].split('.')[1])

    path = os.path.join(folder, fixed_filename)
    logger.info(f"Loading from {path}")

    config = {}
    if params and 'dtype' in params:
        config['dtype'] = params['dtype']

    if filename.endswith('.csv'):
        return pd.read_csv(path, sep=';', **config)
    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        return pd.read_excel(path, **config)
    elif filename.endswith('.json'):
        return json.load(open(path, 'r'))
    elif filename.endswith('.shp'):
        return gpd.read_file(path)
    elif filename.endswith('.zip'):
        return ZipFile(path, 'r')

    return None


def find_last_version(folder, filename, version=-1, max_version=-1):
    """
    Retrieve the latest version of the filename in the folder.

    :param folder: where the file is searched
    :param filename: filename to find the version
    :return: latest version
    @param version:
    @param max_version:
    """

    filename_without_extension = filename.split(sep)[-1].split('.')[0]
    path_appendix = sep.join(filename.split(sep)[:-1])

    # Use a regex to find the files that are compatible with the filename
    file_list = glob.glob(rf'{os.path.join(folder, path_appendix, filename_without_extension)}_v*')

    # Extract from the name of the file the version and create an array of versions
    versions = [int(re.search('_v(\d+).', file).group(1)) for file in file_list]

    if version > -1 and version in versions:
        return version

    if max_version > 0:
        versions = [v for v in versions if v < max_version]

    # The last version is the last item in the array of versions otherwise None
    return max(versions) if versions else None


def find_last_run_id(folder, filename):
    """
    Retrieve the latest version of the filename in the folder.

    :param folder: where the file is searched
    :param filename: filename to find the version
    :return: latest version
    """

    filename_without_extension = filename.split(sep)[-1].split('.')[0]
    path_appendix = sep.join(filename.split(sep)[:-1])

    # Use a regex to find the files that are compatible with the filename
    file_list = glob.glob(rf'{os.path.join(folder, path_appendix, filename_without_extension)}_vX_r*')

    # Extract from the name of the file the version and create an array of versions
    ids = [int(re.search('_v0_r(\d+).', file).group(1)) for file in file_list]

    # Sort the array version
    ids = (max(ids) if ids else 0) + 1

    return ids


class StorageManager:
    """
    Class that manages the output. It handles the local storage.
    """

    def __init__(self, configuration):
        """
        Class constructor.

        @param local_source: source folder in the local device
        @param local_destination: destination folder in the local devide
        """

        # Save the configuration
        self.configuration = configuration

        # Set local repository
        self.local_source = self.validate_and_create_path(folder=configuration['local_repo']['source'], force=True)
        self.local_destination = self.validate_and_create_path(folder=configuration['local_repo']['destination'],
                                                               force=True)

        # Set remote repository
        remote_type = configuration['remote_repo']['type']
        if remote_type == 'teams':
            remote_source = configuration['remote_repo']['source']
            remote_destination = configuration['remote_repo']['destination']

        self.remote_type = remote_type
        self.remote_source = remote_source
        self.remote_destination = remote_destination

        # logger.info('Local source folder: {}'.format(local_source))
        # logger.info('Local destination folder: {}'.format(local_destination))

        # Maps the slug of the component with the destination path
        self.destination_map = {}

        # Run parameters
        self.version = None
        self.run_id = None

        # Initialize the database if it is used
        self.database = None
        self.configure_database()

    def get_database_instance(self):
        """
        Retrieve the instance of the database.

        @return: database instance
        """

        return self.database

    def configure_database(self):
        """
        Configure the database on the base of the configuration.
        @return: database object
        """

        # In the case the configuration is not available
        if "database" not in self.configuration:
            return False

        # Get the configuration of the database
        database_configuration = self.configuration['database']

        # Get the signature of the database
        signature = database_configuration['signature']

        # Oracle case
        if 'oracle' in signature.lower():
            self.database = Oracle(ip_address=database_configuration['ip_address'],
                                   port=database_configuration['port'],
                                   sid=database_configuration['sid'],
                                   service_name=database_configuration['service_name'],
                                   username=database_configuration['username'],
                                   password=database_configuration['password'],
                                   drivers=database_configuration['drivers'])

        return True

    def fetch_query(self, query, params=None):
        """
        Execute a query on the database to extract data.

        @param query: fetching query
        @return: query output
        """

        result = self.database.fetch(query=query)

        try:
            if params:

                if 'as_dataframe' in params and params['as_dataframe'] == True:
                    table_name = re.findall(r"(?<=FROM )(.+?)((?=WHERE)|$)", query)[0][0]
                    header_query = f"SELECT column_name FROM USER_TAB_COLUMNS WHERE table_name = '{table_name}' ORDER BY COLUMN_ID"
                    header = self.database.fetch(header_query)
                    result = pd.DataFrame(result, columns=[c[0] for c in header])

        except:
            pass

        return result

    def write_query(self, query):
        """
        Execute a query on the database to write data.

        @param query: writing query
        @return: True
        """

        # Make the push query
        results = self.database.push(query=query)

        # In the case there is an error during the query execution, the exception is retrieved
        if not results[0]:
            logger.error("Error while executing a query {} - {}".format(query[:15], results[1]))

        return True

    def write_many(self, table, dataset):
        """
        Execute a batch insert in the table specified.

        @param table: target table
        @param dataset: to be written
        @return: True or False
        """

        # Make the push query
        results = self.database.push_many(table=table, dataset=dataset)

        # In the case there is an error during the query execution, the exception is retrieved
        if not results[0]:
            logger.error("Error while executing a query {}".format(results[1]))

        return True

    def export_to_database(self, queries):

        # List of queries to be executed atomically
        single_queries = queries['query']

        # List of batch queries to be executed
        batch_queries = queries['batch']

        # Iterate over all outputs and exports each one
        for i, query in enumerate(single_queries):
            self.write_query(query=query)

        for i, bundle in enumerate(batch_queries):
            table = bundle[0]  # Name of the table
            dataset = bundle[1]  # Dataset to be inserted in batch
            self.write_many(table=table, dataset=dataset)

        return True

    def get_file(self, filename, params=None, version=-1):
        """
        Return (if exists) the file corresponding to the filename in input. Zoe selects
        automatically the version you need, otherwise return the latest one.

        :param filename: name of the file to be loaded
        :param version: version of the file to be loaded
        :return: file content
        """

        try:
            return read_file(folder=self.local_source, params=params, filename=filename, version=version)
        except (FileNotFoundError, DriverError) as e:
            return read_file(folder=self.local_destination, params=params, filename=filename, version=version,
                             max_version=self.version if self.version else -1)

    def get_folder_files(self, folder_name, params=None, version=-1):
        """
        Return (if exists) all files in the folder corresponding to the name in input. Zoe selects
        automatically the version you need, otherwise return the latest one.

        :param folder_name: name of the folder to be loaded
        :param version: version of the file to be loaded
        :param params: list of additional parameters expressed by the user
        :return: file content
        """

        filename = '*'

        # In case the user provides a specific extension it is added to the filename to be searched
        if params and 'extension' in params:
            filename += params['extension']

        # Search all file matching user input
        file_list = glob.glob(rf'{os.path.join(self.local_destination, *folder_name, filename)}')

        cleaned_file_list = []
        for file in file_list:
            tmp_name = file.split('_v')[0] + '.csv'
            if tmp_name not in cleaned_file_list:
                cleaned_file_list.append(tmp_name)

        # List of read files
        imported_files = []

        # For each file in file list: read
        for file in cleaned_file_list:
            try:
                imported_files.append(read_file(folder=self.local_source, filename=file, version=version))
            except (FileNotFoundError, DriverError) as e:
                imported_files.append(read_file(folder=self.local_destination, filename=file, version=version,
                                                max_version=self.version if self.version else -1))

        return imported_files

    def export_to_storage(self, outputs, slug):

        # For each output find or create the output name
        outputs, output_names = define_output_names(outputs, self.destination_map[slug], slug)

        # Iterate over all outputs and exports each one
        for i, output in enumerate(outputs):
            self.export_output(output, output_names[i])

        return True

    def export_output(self, output, output_name):
        """
        Export the output from the function of the component.
        """

        version = self.version
        run_id = self.run_id

        # Version 0 is the reserved version for local mode
        if version == 0:

            # Try to search an already existing versioning pattern, if not it is assigned run_id equal to 0
            try:
                run_id = find_last_run_id(folder='', filename=output_name)
            except:
                run_id = 0

        # Compile the filename
        fixed_filename = output_name.split('.')[0] + '_v{}.csv'.format(version)

        path = fixed_filename
        # DataFrame case
        if isinstance(output, pd.DataFrame):
            export_csv(output, path)
            logger.success('Exported dataset \'{}\' in \'{}\'.'.format(fixed_filename, self.local_destination))

        # All other cases
        else:
            logger.info('Output format not supported yet!')

    def validate_and_create_path(self, folder, prefix=None, force=True):
        """
        Check if the path points to a folder and validates it.
        """

        path = folder if not prefix else os.path.join(prefix, folder)

        # Check if the path is a folder path or a file path.
        if '.' in path.split(os.sep)[-1]:
            logger.log("'{}' is file path, please provide a folder path.".format(path), terminate=True)

        # Check if the path exists.
        if not os.path.isdir(path):

            # If the force flag is not set, the execution terminates.
            if not force:
                logger.log("'{}' is not a valid path.".format(path), terminate=True)

            # The folder is created.
            os.mkdir(path=path)

        return path

    def create_sub_destination_folder(self, folder, id):
        """
        Create the root folder for the component outputs.

        @param folder: path
        @return: path validated
        """

        self.destination_map[id] = self.validate_and_create_path(folder, self.local_destination)

        return self.destination_map[id]

    def configure(self, version, run_id):
        """
        Configure the storage manager with the parameters of the current run.

        @param version: current version
        @param run_id: current run ID
        """

        # If the response from the server is negative, the engine is running in local mode,
        # for this reason the version used is 0 and the run_id is temporarily assigned to 0.
        if not version or not run_id:
            version = 0
            run_id = 0

        # Otherwise the version and the run_id is provided by the server
        self.version = version
        self.run_id = run_id

        return self.version, self.run_id
