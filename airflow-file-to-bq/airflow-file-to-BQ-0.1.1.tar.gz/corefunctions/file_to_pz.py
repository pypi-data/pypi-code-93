from airflow.operators.python import PythonOperator
from file_to_lz import FileToLZOperator
from lz_to_sz import LZToSZOperator
from sz_to_pz_scd1 import SZToPZOperatorSCD1
from sz_to_pz_scd2 import SZToPZOperatorSCD2


class FileToPZOperatorSCD1(PythonOperator):
    def __init__(self, project: str, google_project: str, data_bucket: str, data_filename_prefix: str, data_filename: str, field_delimiter: str, *args, **kwargs) -> None:
        # Call of the actual PythonOperator
        def file_to_PZ(project: str, google_project: str, data_bucket: str, data_filename: str, data_filename_prefix: str, *args, **kwargs) -> None:
            step1 = FileToLZOperator(project=project,
                                     google_project=google_project,
                                     data_bucket=data_bucket,
                                     data_filename_prefix=data_filename_prefix,
                                     data_filename=data_filename,
                                     source_format='CSV',
                                     field_delimiter='#',
                                     skip_leading_rows=1,
                                     write_disposition='WRITE_TRUNCATE',
                                     autodetect=False)
            step1.execute(kwargs)

            step2 = LZToSZOperator(project=project,
                                   google_project=google_project,
                                   data_filename=data_filename,
                                   use_legacy_sql=False,
                                   write_disposition='WRITE_TRUNCATE',
                                   location="europe-west3")
            step2.execute(kwargs)

            step3 = SZToPZOperatorSCD1(project=project,
                                       google_project=google_project,
                                       data_filename=data_filename,
                                       use_legacy_sql=False,
                                       write_disposition='WRITE_TRUNCATE',
                                       location="europe-west3")
            step3.execute(kwargs)

        PythonOperator.__init__(self,
                                task_id='complete_load',
                                python_callable=file_to_PZ,
                                provide_context=True,
                                op_kwargs={
                                    'project': project,
                                    'google_project': google_project,
                                    'data_bucket': data_bucket,
                                    'data_filename_prefix': data_filename_prefix,
                                    'data_filename': data_filename,
                                    'source_format': 'CSV',
                                    'field_delimiter': field_delimiter,
                                    'skip_leading_rows': 1,
                                    'write_disposition': 'WRITE_TRUNCATE',
                                    'autodetect': False},
                                dag=dag)
