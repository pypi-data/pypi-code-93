# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_source_registration_params
import cohesity_management_sdk.models_v2.register_physical_sever_request_parameters
import cohesity_management_sdk.models_v2.register_cassandra_source_request_parameters
import cohesity_management_sdk.models_v2.register_mongo_db_source_request_parameters
import cohesity_management_sdk.models_v2.register_couchbase_source_request_parameters
import cohesity_management_sdk.models_v2.register_hdfs_source_request_parameters
import cohesity_management_sdk.models_v2.register_h_base_source_request_parameters
import cohesity_management_sdk.models_v2.register_hive_source_request_parameters

class SourceRegistration(object):

    """Implementation of the 'Source Registration.' model.

    Specifies the Source Registration.

    Attributes:
        id (long|int): Source Registration ID. This can be used to retrieve,
            edit or delete the source registration.
        source_id (long|int): ID of top level source object discovered after
            the registration.
        environment (Environment8Enum): Specifies the environment type of the
            Protection Source.
        name (string): A user specified name for this source.
        vmware_params (VmwareSourceRegistrationParams): Specifies the
            paramaters to register a VMware source.
        physical_params (RegisterPhysicalSeverRequestParameters): Specifies
            parameters to register physical server.
        cassandra_params (RegisterCassandraSourceRequestParameters): Specifies
            parameters to register cassandra source.
        mongodb_params (RegisterMongoDBSourceRequestParameters): Specifies
            parameters to register MongoDB source.
        couchbase_params (RegisterCouchbaseSourceRequestParameters): Specifies
            parameters to register Couchbase source.
        hdfs_params (RegisterHDFSSourceRequestParameters): Specifies
            parameters to register an HDFS source.
        hbase_params (RegisterHBaseSourceRequestParameters): Specifies
            parameters to register an HBase source.
        hive_params (RegisterHiveSourceRequestParameters): Specifies
            parameters to register Hive source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "source_id":'sourceId',
        "environment":'environment',
        "name": 'name',
        "vmware_params":'vmwareParams',
        "physical_params":'physicalParams',
        "cassandra_params":'cassandraParams',
        "mongodb_params":'mongodbParams',
        "couchbase_params":'couchbaseParams',
        "hdfs_params":'hdfsParams',
        "hbase_params":'hbaseParams',
        "hive_params":'hiveParams'
    }

    def __init__(self,
                 id=None,
                 source_id=None,
                 environment=None,
                 name=None,
                 vmware_params=None,
                 physical_params=None,
                 cassandra_params=None,
                 mongodb_params=None,
                 couchbase_params=None,
                 hdfs_params=None,
                 hbase_params=None,
                 hive_params=None):
        """Constructor for the SourceRegistration class"""

        # Initialize members of the class
        self.id = id
        self.source_id = source_id
        self.environment = environment
        self.name = name
        self.vmware_params = vmware_params
        self.physical_params = physical_params
        self.cassandra_params = cassandra_params
        self.mongodb_params = mongodb_params
        self.couchbase_params = couchbase_params
        self.hdfs_params = hdfs_params
        self.hbase_params = hbase_params
        self.hive_params = hive_params


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        id = dictionary.get('id')
        source_id = dictionary.get('sourceId')
        environment = dictionary.get('environment')
        name = dictionary.get('name')
        vmware_params = cohesity_management_sdk.models_v2.vmware_source_registration_params.VmwareSourceRegistrationParams.from_dictionary(dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None
        physical_params = cohesity_management_sdk.models_v2.register_physical_sever_request_parameters.RegisterPhysicalSeverRequestParameters.from_dictionary(dictionary.get('physicalParams')) if dictionary.get('physicalParams') else None
        cassandra_params = cohesity_management_sdk.models_v2.register_cassandra_source_request_parameters.RegisterCassandraSourceRequestParameters.from_dictionary(dictionary.get('cassandraParams')) if dictionary.get('cassandraParams') else None
        mongodb_params = cohesity_management_sdk.models_v2.register_mongo_db_source_request_parameters.RegisterMongoDBSourceRequestParameters.from_dictionary(dictionary.get('mongodbParams')) if dictionary.get('mongodbParams') else None
        couchbase_params = cohesity_management_sdk.models_v2.register_couchbase_source_request_parameters.RegisterCouchbaseSourceRequestParameters.from_dictionary(dictionary.get('couchbaseParams')) if dictionary.get('couchbaseParams') else None
        hdfs_params = cohesity_management_sdk.models_v2.register_hdfs_source_request_parameters.RegisterHDFSSourceRequestParameters.from_dictionary(dictionary.get('hdfsParams')) if dictionary.get('hdfsParams') else None
        hbase_params = cohesity_management_sdk.models_v2.register_h_base_source_request_parameters.RegisterHBaseSourceRequestParameters.from_dictionary(dictionary.get('hbaseParams')) if dictionary.get('hbaseParams') else None
        hive_params = cohesity_management_sdk.models_v2.register_hive_source_request_parameters.RegisterHiveSourceRequestParameters.from_dictionary(dictionary.get('hiveParams')) if dictionary.get('hiveParams') else None

        # Return an object of this model
        return cls(id,
                   source_id,
                   environment,
                   name,
                   vmware_params,
                   physical_params,
                   cassandra_params,
                   mongodb_params,
                   couchbase_params,
                   hdfs_params,
                   hbase_params,
                   hive_params)


