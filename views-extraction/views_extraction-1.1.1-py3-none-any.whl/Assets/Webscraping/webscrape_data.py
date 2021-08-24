import json
import math
import multiprocessing
import sys
from time import time

from Assets.Webscraping.worker import Worker
from constants import *


class WebscrapeData:
    def __init__(self, username, password):
        self.save_worker_files = SAVE_WORKER_FILES
        self.manager, self.namespace = self.create_manager()
        self.namespace.data = []
        self.number_of_workers = self.generate_number_of_workers()
        self.json_file_path = OUTPUT_NAME
        self.json_file = self.read_json()
        self.all_chunks, self.number_of_dictionaries = self.split_json()
        self.username, self.password = (username, password)
        self.worker_instances = []
        self.workers = self.create_number_of_workers()
        self.all_lists = None
        self.process_file_path = OUTPUT_FOLDER

    @staticmethod
    def create_manager():
        manager = multiprocessing.Manager()
        namespace = manager.Namespace()
        return manager, namespace

    @staticmethod
    def generate_number_of_workers() -> int:
        return NUMBER_OF_THREADS

    def read_json(self):
        with open(self.json_file_path, 'r') as file:
            data = json.load(file)
        return data

    def split_json(self) -> list:
        number_of_dictionaries = math.ceil(
            len(self.json_file) / self.number_of_workers)
        dictionaries = self.json_file
        list_of_chunks = []
        [list_of_chunks.append(dictionaries[chunk_idx:chunk_idx + number_of_dictionaries])
         for chunk_idx in range(0, len(self.json_file), number_of_dictionaries)]
        return list_of_chunks, len(self.json_file)

    def create_number_of_workers(self):
        try:
            return [multiprocessing.Process(
                target=self.worker_main,
                args=(
                    self.namespace,
                    worker,
                    self.username,
                    self.password,
                    self.all_chunks[worker]
                )
            ) for worker in range(self.number_of_workers)]
        except IndexError:
            print("[IndexError] There are more workers than data.")
            print("Try reducing the number of workers.")
            sys.exit()

    @staticmethod
    def worker_main(namespace, position: int, username: str, password: str, json_list: list):
        worker_inst = Worker(namespace, position,
                             username, password, json_list)
        worker_inst.main()

    def start_workers(self):
        for worker in self.workers:
            worker.start()

    def join_workers(self):
        for worker in self.workers:
            worker.join()

    @staticmethod
    def get_process_files(folder_path):
        """Gather all of the json file paths into one list from the output folder"""
        return [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.startswith("output_") and file.endswith(".json")
        ]

    def retrieve_lists(self) -> list:
        """Return all the lists from Manager's namespace or from worker files."""
        if self.save_worker_files:
            all_data = []
            all_files = self.get_process_files(self.process_file_path)
            for file in all_files:
                with open(file, 'r') as file_inst:
                    data = json.load(file_inst)
                    for post in data:
                        all_data.append(post)
        else:
            all_data = self.namespace.data
        return all_data

    def save_json(self):
        with open(self.json_file_path, 'w+') as file:
            json.dump(self.all_lists, file, indent=4)

    def main(self):
        program_start_time = time()
        self.start_workers()
        self.join_workers()
        self.all_lists = self.retrieve_lists()
        self.save_json()
        program_end_time = time()
        print("Webscraping Data took {} seconds to execute.".format(
            program_end_time - program_start_time))


if __name__ == '__main__':
    start_time = time()
    main_inst = WebscrapeData("", "")
    main_inst.main()
    end_time = time()
    print("The program took {} seconds to execute.".format(end_time - start_time))
