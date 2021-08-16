from  pyspark.sql.functions import lit,col
import os
import boto3
from functools import reduce



class AddTableToGlue(object):

    def __init__(self ,df ,database_name_of_output ,table_name_of_output ,path_of_output_file="s3://ph-platform/2020-11-11/etl/temporary_files/",mode="overwrite",share_num=1):

        self.cmd_name = "glue"
        self.region_name = "cn-northwest-1"
        self.client = boto3.client(self.cmd_name, self.region_name)
        self.df = df
        self.share_num = self.get_share_num(share_num)
        self.mode = self.get_mode_of_write(mode)

        self.path_of_output_file = self.get_path_of_output_file(path_of_output_file)

        self.database_name = self.get_DatabaseName(database_name_of_output)
        self.table_name = self.get_TableName(table_name_of_output)
        self.path_of_output = self.get_path_of_output(path_of_output_file ,table_name_of_output)


    def get_DatabaseName(self ,database_name):

        database_name = str(database_name)

        return database_name

    def get_TableName(self ,table_name):

        table_name = str(table_name)

        return table_name

    def get_mode_of_write(self,mode):
        '''
        :param mode: mode for file write
        :return:
        '''

        if mode:
            mode = str(mode).lower()
        else:
            mode = "overwrite"
        return mode

    def get_share_num(self,share_num):
        '''
        :param share_num: number of file partitions and default is 1
        :return:
        '''
        if share_num:
            share_num = int(share_num)
        else:
            share_num = 1
        return share_num

    def get_path_of_output_file(self,path_of_output_file):
        '''
        :param path_of_output_file: file path for writing to S3
        :return:
        '''

        if path_of_output_file:
            path_of_output_file = str(path_of_output_file)
        else:
            path_of_output_file = "s3://ph-platform/2020-11-11/etl/temporary_files/"
        return path_of_output_file


    # --检查表名
    def exist_table_name(self ,table_name ,database_name):

        response =  self.client.get_tables(
            DatabaseName = database_name,
        )

        table_lists_of_database = list(map(lambda x: x["Name"] ,response["TableList"]))

        if table_name in table_lists_of_database:
            singal_of_table = True
        else:
            singal_of_table = False

        return singal_of_table


    def get_args_of_list(self ,col_list):

        list_ = ["Name" ,"Type"]
        schema_of_args = list(map(lambda x :dict(zip(list_ ,list(x))) ,col_list))

        return schema_of_args

    # --创建表
    def create_table(self ,location ,args_of_col ,args_of_partition):
        print(f"在数据库:{self.database_name} 创建表-->> {self.table_name}...")
        try:
            create_table_info = self.client.create_table(
                DatabaseName=self.database_name,
                TableInput = {
                    "Name" :self.table_name,
                    "StorageDescriptor" :{
                        "Location" :location,
                        "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                        "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                        "SerdeInfo" :{
                            "SerializationLibrary" :"org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                        },
                        "Columns" :args_of_col,
                    },
                    'PartitionKeys': args_of_partition,
                    "TableType": "EXTERNAL_TABLE",
                },

            )
            print(f"{self.table_name} 创建完毕")
        except Exception as e:
            print(e)
            create_table_info = None
        return create_table_info

    def create_partition(self ,partition_input_list):

        print(f"开始在数据库:{self.database_name} -->> 表:{self.table_name} 写入数据...")
        try:

            glue_info = self.client.batch_create_partition(DatabaseName=self.database_name ,TableName=self.table_name
                                                           ,PartitionInputList=partition_input_list)

            print(f"数据已写入{self.database_name} -->> {self.table_name}\n")
        except Exception as e:
            print(e)
            print(f"数据写入{self.database_name} -->> {self.table_name} 失败\n")
            glue_info = None

        return glue_info

    def get_path_of_output(self ,path_of_output ,table_name):

        path_of_output = os.path.join(path_of_output ,table_name)

        return path_of_output

    # --写入路径
    def write_to_path(self ,df ,col_of_partitionBy ,path_of_write):

        try:
            df.repartition(self.share_num).write.format("parquet").mode(self.mode).partitionBy \
                (col_of_partitionBy).parquet(path_of_write)
            write_info = f"{path_of_write} 写入成功"
        except Exception as e:
            print(e)
            write_info = f"{path_of_write} 写入失败"
        print(write_info)
        return write_info

    def add_col_of_partition(self ,df ,dict_of_partition):

        if len(dict_of_partition) == 0:
            pass
        else:
            for k ,v in dict_of_partition.items():

                df = df.withColumn(str(k) ,lit(v))

        return df

    def get_location(self ,path_of_prefix ,dict_of_partition):


        location_list = list(dict_of_partition.items())

        if len(location_list) == 0:
            location = path_of_prefix
        else:
            location_path = list(map(lambda x: str(x[0]) + "=" + str(x[1]) ,location_list))

            location = reduce(lambda x ,y: os.path.join(x ,y) ,location_path)

            location = os.path.join(path_of_prefix ,location)

        return location


    def get_info_of_PartitionInputList(self ,value_of_partition_input ,location):

        partition_input_list = [{
            "Values" :value_of_partition_input,
            "StorageDescriptor": {
                "SerdeInfo": {
                    "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
                },
                "Location": location,
            }
        }]

        return partition_input_list

    def get_args_of_dict(self ,dict_of_input):

        key_list = list(dict_of_input.keys())

        value_list = list(dict_of_input.values())

        value_list =  list(map(lambda x: str(x) if x == None else x ,value_list))

        dict_of_output = dict(zip(key_list ,value_list))

        return key_list ,value_list ,dict_of_output

    def get_schema_of_table(self,df):

        schema_of_table = df.dtypes

        return schema_of_table

    def get_arg_of_glue(self,schema_of_table,col_of_partitionBy):

        dict_of_schema = dict(schema_of_table)

        schema_of_partition = list(map(lambda x :(x ,dict_of_schema[x]) , col_of_partitionBy))

        schema_of_col = [ x for x in schema_of_table if x not in schema_of_partition]

        args_of_partition = self.get_args_of_list(schema_of_partition)

        args_of_col = self.get_args_of_list(schema_of_col)

        return args_of_partition ,args_of_col

    # --添加表至aws glue
    def add_table_to_aws_glue(self ,partition_input_list ,location ,args_of_col ,args_of_partition):
        singal = self.exist_table_name(self.table_name ,self.database_name)
        if singal == True:
            print(f"{self.table_name} Already exists")
            info = self.create_partition(partition_input_list)
        else:
            if len(args_of_partition) == 0:
                print("no partition col, just write data to table. ")
                info = self.create_table(location ,args_of_col ,args_of_partition)
            else:
                print(f"{self.table_name} not exist, start creating...")
                info = self.create_table(location ,args_of_col ,args_of_partition)
                info = self.create_partition(partition_input_list)

        return info


    def add_info_of_partitionby(self ,dict_of_partition):

        # --分区字典
        col_of_partitionBy ,value_of_partition_input ,dict_of_partition = self.get_args_of_dict(dict_of_partition)

        # ---填入分区信息

        df = self.add_col_of_partition(self.df ,dict_of_partition)

        # ---写入路径
        self.write_to_path(df ,col_of_partitionBy ,self.path_of_output)

        # ---获取location

        location = self.get_location(self.path_of_output ,dict_of_partition)

        partition_input_list = self.get_info_of_PartitionInputList(value_of_partition_input ,location)

        # ---获取schema参数
        # --table schema
        schema_of_table = self.get_schema_of_table(df)

        args_of_partition ,args_of_col = self.get_arg_of_glue(schema_of_table ,col_of_partitionBy)

        # ---写入表
        info = self.add_table_to_aws_glue(partition_input_list ,location ,args_of_col ,args_of_partition)

        return info