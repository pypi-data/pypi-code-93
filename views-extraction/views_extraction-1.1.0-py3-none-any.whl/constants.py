import os
import psutil

OUTPUT_NAME: str = os.path.join(os.path.dirname(
    os.path.realpath(__file__))) + "/Output/data.json"
OUTPUT_FOLDER: str = os.path.join(
    os.path.dirname(os.path.realpath(__file__))) + '/Output'
SUMMATION_FILE: str = os.path.join(os.path.dirname(
    os.path.realpath(__file__))) + '/Output/Summation'
INVALID_IDS_FILE_PATH: str = os.path.join(os.path.dirname(
    os.path.realpath(__file__))) + '/Output/Invalid_Ids'
SAVE_WORKER_FILES: bool = True
NUMBER_OF_THREADS: int = psutil.cpu_count() * 2
ALTERABLE_CONSTANTS = True
OUTPUT_TYPE: str = 'excel'  # Options: csv, excel, json
RECIPIENT: str = 'abhisar.muz@gmail.com, srinivassriram06@gmail.com'
EMAIL_FROM: str = 'ereaders.visitors@gmail.com'
PASSWORD: str = ''
