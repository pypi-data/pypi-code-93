from cygnsslib.data_downloader.download_cygnss import download_file
import os
import shutil
import zipfile

ANT_PTRN_URL = 'https://bitbucket.org/usc_mixil/cygnss_antenna_patterns/get/master.zip'


def download_cyg_antenna_patterns(antenna_patterns_folder_path=None):
    if antenna_patterns_folder_path is None:
        antenna_patterns_folder_path = os.path.join(os.environ["CYGNSS_PATH"], 'cygnss_antenna_patterns')
    if not os.path.isdir(antenna_patterns_folder_path):
        os.makedirs(antenna_patterns_folder_path)

    files_list = os.listdir(antenna_patterns_folder_path)
    if 'antennaRx_CYGNSS_Obs1_Nadir02_Starboard_processed' in files_list and 'antennaRx_CYGNSS_Obs1_Nadir01_Port_processed' in files_list:
        ant_ptrn_files_path = [os.path.join(antenna_patterns_folder_path, 'antennaRx_CYGNSS_Obs1_Nadir02_Starboard_processed'),
                               os.path.join(antenna_patterns_folder_path, 'antennaRx_CYGNSS_Obs1_Nadir01_Port_processed')]
        return ant_ptrn_files_path

    ant_ptrn_zip_path = os.path.join(antenna_patterns_folder_path, ANT_PTRN_URL.split('/')[-1])
    if not os.path.exists(ant_ptrn_zip_path):
        ant_ptrn_zip_path = download_file(ANT_PTRN_URL, antenna_patterns_folder_path, auth=None)

    ant_ptrn_files_path = extract_ant_ptrn_zip(ant_ptrn_zip_path, antenna_patterns_folder_path)
    os.remove(ant_ptrn_zip_path)  # remove zip file
    return ant_ptrn_files_path


def extract_ant_ptrn_zip(zip_file_path, out_path):

    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:

        files_list = zip_ref.namelist()
        extracted_files = list()
        for file_name in files_list:
            if file_name.endswith('processed'):
                zip_ref.extract(file_name, path=out_path)
                shutil.move(os.path.join(out_path, file_name), os.path.join(out_path, file_name.split(os.sep)[-1]))
                extracted_files.append(os.path.join(out_path, file_name.split(os.sep)[-1]))

    os.rmdir(os.path.join(out_path, file_name.split(os.sep)[0]))
    return extracted_files


if __name__ == '__main__':
    download_cyg_antenna_patterns()
