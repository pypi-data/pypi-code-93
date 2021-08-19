import sys
import os
from os import path, sep, getcwd
import importlib
import time
import shutil
from time_study_preprocessing_main import preprocessing_all_uema

device = 'phone'
module_name = '.time_study_preprocessing_main'
information_text_file_path = getcwd() + sep + "analysis_task" + sep + device + "_information_included.txt"
information_list = ["app_usage", "app_use_duration", "battery", "daily_notes", "detected_activity", "GPS",
                    "notif_logs", "phone_broadcasts", "prompt_response", "step_count", "wifi_state",
                    "apps_installed", "daily_report"]


def preprocessing_start(microT_root_path, intermediate_file_save_path, decrypt_password,
                        delete_raw, date_start, date_end):
    # parse information and participants text file
    # information_list = preprocess_scripts.utils.parse_information.parse_information(information_text_file_path)
    p_id_list = []
    # first check if participant list string ends with .txt. If it is .txt use the code below or else just add that
    # to the list
    # if participant_text_file_path.endswith('.txt'):
    #     p_id_list = preprocess_scripts.utils.parse_participants.parse_participants(participant_text_file_path)
    # else:
    #     p_id_with_domain = participant_text_file_path + '@timestudy_com'
    #     p_id_list.append(p_id_with_domain)

    t0 = time.time()
    # for p_id in p_id_list:
    # print("Phone pre-processing for: " + str(p_id))
    # iterate through participants
    # p_id_logs = microT_root_path + sep + p_id + sep + 'logs'
    # p_id_data = microT_root_path + sep + p_id + sep + 'data'
    p_id_logs = microT_root_path + sep + 'logs'
    p_id_data = microT_root_path + sep + 'data'
    root_path_components = microT_root_path.split(sep)
    p_id = root_path_components[len(root_path_components) - 1]

    if path.exists(p_id_logs):
        date_list = time_study_preprocessing_main.preprocess_scripts.utils.validate_dates.get_relevant_date_list(p_id_logs, date_start, date_end)
        for date in date_list:
            for info in information_list:
                module_path = "preprocess_scripts." + device + '.' + info
                preprocess_module = importlib.import_module(module_name, module_path)
                # pre-process
                preprocess_module.pre_process(microT_root_path, intermediate_file_save_path, p_id, decrypt_password,
                                              date)
            if delete_raw == "1":
                p_id_logs_date = p_id_logs + sep + date
                p_id_data_date = p_id_data + sep + date
                if path.exists(p_id_logs_date):
                    shutil.rmtree(p_id_logs_date)
                if path.exists(p_id_data_date):
                    shutil.rmtree(p_id_data_date)
        if delete_raw == "1":
            if len(os.listdir(p_id_logs)) == 0:
                shutil.rmtree(p_id_logs)
            if len(os.listdir(p_id_data)) == 0:
                shutil.rmtree(p_id_data)

    t1 = time.time()
    print("Time elapsed is  {} secs : \n".format((t1 - t0)))


if __name__ == "__main__":
    # parse arguments
    try:
        argv = sys.argv[1:]
        microT_root_path, intermediate_file_save_path, decrypt_password, delete_raw, \
        date_start, date_end, hourKeep = time_study_preprocessing_main.preprocess_scripts.utils.parse_cml_argv.parse_arguments_ema(argv)
    except:
        time_study_preprocessing_main.preprocess_scripts.utils.parse_cml_argv.printHelpOptions()
        sys.exit(
            'Errors : Incorrect Command Line Arguments. Please correct your arguments according to the references '
            'above.')

    # pre processing
    preprocessing_start(microT_root_path, intermediate_file_save_path, decrypt_password,
                        delete_raw, date_start, date_end)
    # python_version = str(sys.version_info.major) + "." + str(sys.version_info.minor) os.system( 'python' +
    # python_version + ' preprocessing_all_uema.py ' + microT_root_path + " " + intermediate_file_save_path + " " +
    # participant_text_file_path + " " + delete_raw + " " + date_start + " " + date_end)

    # watch preprocessing
    preprocessing_all_uema.main(microT_root_path, intermediate_file_save_path, delete_raw, date_start, date_end)

    # output summary report
    # if date_start == date_end:
    time_study_preprocessing_main.preprocess_scripts.utils.output_summary_report.generate_output_report(microT_root_path, intermediate_file_save_path,
                                                                                                        date_start)
