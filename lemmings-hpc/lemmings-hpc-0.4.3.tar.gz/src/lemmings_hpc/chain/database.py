"""
Different usefull functions to interact with the database.yml file
"""
import os
import pkg_resources  # part of setuptools
from datetime import datetime
import time
from pathlib import Path

import yaml
from prettytable import PrettyTable
import numpy as np

DATABASE_ACCESSED = False

class Database:
    """Abstraction to interact with the database"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = './database.yml'
        self.db_path = db_path
        self._initialise_db()

    @property
    def _database(self):
        """
        Get the informations from the database.yml file.*
        """

        with open(self.db_path) as fin:
            database = yaml.load(fin, Loader=yaml.FullLoader)
        return database

    @property
    def latest_chain_name(self):
        """Get the last chain name"""
        try:
            out = sorted(self._database, key=self.get_datetime)[-1]
        except IndexError:
            print("There is no chain in the Database 'database.yml'")
        return out

    @property
    def count(self):
        """
        *Get the loop number of a chain*
        """
        return int(len(self._database[self.latest_chain_name]))

    def _initialise_db(self):
        """
        *Create a Database if doesn't exist.*
        """
        if not Path(self.db_path).is_file():
            database = {}
            with open(self.db_path, 'w') as fout:
                yaml.dump(database, fout, sort_keys=False)

    def get_datetime(self, chain_name):
        """
        *Get the datetime of the first loop of a chain*
        """
        database = self._database
        time = database[chain_name][0]['datetime']
        datetime_obj = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

        return datetime_obj

    def initialise_new_chain(self, chain_name):
        """
        *Create a new chain dict{ } in the DB*
        """
        version = str(pkg_resources.require("lemmings_hpc")[0].version)
        database = self._database

        database[chain_name] = [{'lemmings_version': version,
                                 'datetime': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                 'safe_stop': False,
                                 'submit_path': './'}]
        with open(self.db_path, 'w') as fout:
            yaml.dump(database, fout, sort_keys=False)

    def initialise_new_loop(self):
        """Create a new loop in a chain"""
        database = self._database
        database[self.latest_chain_name].append({'datetime': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),  # pylint: disable=line-too-long
                                                 'safe_stop': False,
                                                 'submit_path': './'})

        with open(self.db_path, 'w') as fout:
            yaml.dump(database, fout, sort_keys=False)

    def add_nested_level_to_loop(self, key):
        """ Add a nested level in database
            TODO:
                1) add loop options
                2) use Nob if more nested levels will be present
        """
        database = self._database
        loop_num = self.get_current_loop_val('loop_count')
        database[self.latest_chain_name][loop_num -1][key] = []

        with open(self.db_path, 'w') as fout:
            yaml.dump(database, fout, sort_keys=False)

    def update_nested_level_to_loop(self, nested_key, key, value):
        """ Add a nested level in database
            TODO: 
                1) add loop options
                2) use Nob if more nested levels will be present
        """
        database = self._database
        loop_num = self.get_current_loop_val('loop_count')
        if database[self.latest_chain_name][loop_num -1][nested_key] == []:
            database[self.latest_chain_name][loop_num -1][nested_key].append({key:value})
        else:
            database[self.latest_chain_name][loop_num -1][nested_key][0][key] = value

        with open(self.db_path, 'w') as fout:
            yaml.dump(database, fout, sort_keys=False)

    def update_loop(self, key, value, index):
        """
        *Update the database of the current folder

        :param index: The loop number of the desired job
        :type index: int
        :param key: The name of the parameter to update or create
        :type key: str
        :param value: The value of the parameter
        :type value: all
        """
        database = self._database
        database[self.latest_chain_name][index - 1][key] = value

        with open(self.db_path, 'w') as fout:
            yaml.dump(database, fout, sort_keys=False)

    def update_current_loop(self, key, value):
        """
        *Update the database of the current folder*

        :param key: The name of the parameter to update or create
        :type key: str
        :param value: The value of the parameter
        :type value: all
        """
        self.update_loop(key, value, self.count)

    def update_previous_loop(self, key, value):
        """
        *Update the database of the current folder*

        :param key: The name of the parameter to update or create
        :type key: str
        :param value: The value of the parameter
        :type value: all
        """
        self.update_loop(key, value, self.count - 1)

    def update_first_loop(self, key, value):
        """
        *Update the database of the current folder*

        :param key: The name of the parameter to update or create
        :type key: str
        :param value: The value of the parameter
        :type value: all
        """
        self.update_loop(key, value, 1)

    def get_loop_val(self, key, index):
        """
        *Get the value of a parameter in a loop of a job.*

        :param key: The name of the parameter to update or create
        :type key: str
        """
        database = self._database
        return database[self.latest_chain_name][index - 1][key]

    def get_current_loop_val(self, key):
        """
        *Get the value of a parameter in a loop of a job.*

        :param key: The name of the parameter to update or create
        :type key: str
        """
        return self.get_loop_val(key, self.count)

    def get_first_loop_val(self, key):
        """
        *Get the value of a parameter in a loop of a job.*

        :param key: The name of the parameter to update or create
        :type key: str
        """
        return self.get_loop_val(key, 1)

    def get_previous_loop_val(self, key):
        """
        *Get the value of a parameter in a loop of a job.*

        :param key: The name of the parameter to update or create
        :type key: str
        """

        return self.get_loop_val(key, self.count - 1)

    def get_chain_names(self):
        """
        *Get chain names from the database*
        """
        return list(self._database.keys())

    def set_progress_quantity(self, value):
        self.update_first_loop('progress_quantity', value)

    def get_current_status(self, keys=None, with_progress = False):
        """
        Function returning the current status of the simulation.
        """
        # keys : is an option that could allow a future control of what to output
        #           but needs to be developed if eventually needed
        status_string = []
        #NOTE: consider using logging package of python

        try:
            database = self._database  # accesses the whole .yaml file
        except FileNotFoundError as excep:
            status_string.append("LemmingsError: " + excep)
            return status_string

        chain_name = self.latest_chain_name
        if chain_name is None:
            raise ValueError("No chain found. Check database.yml file in your current directory ...")

        #--Check first if the database is the main one of a parallel run---#
        parallel_run = False
        try:
            par_dict, = self.get_current_loop_val('parallel_runs')
            parallel_run = True
        except KeyError:
            pass

        if parallel_run:
            if not with_progress:
                table = PrettyTable()
                table.field_names = ["Workflow number", "Status"]
                # match_val = {"start": "S", "hold": "H", "end": 'F'}
                # table.add_rows([[key, match_val[value]] if value in match_val
                #                     else [key, '?'] for key, value in par_dict.items()])

                symbol = {"start": "S", "wait": "W", "end": "F", "error": "E"}
                table.add_rows([(key, symbol.get(val, '?'))
                                for key, val in par_dict.items()])

                # keep for now in case we run with no match issue
                # table.field_names = ["Workflow number", "Status"]
                # for key, value in par_dict.items():
                #     val = "?"
                #     if value == "start":
                #         val = "S"
                #     elif value == "hold":
                #         val = "H"
                #     elif value == "end":
                #         val = "F"
                #     table.add_row([key,val])

                # print("S: Submitted, F: Finished, W: Wait, E: Error")
                # print(table)
                status_string.append("S: Submitted, F: Finished, W: Wait, E: Error")
                status_string.append(table)
                return status_string

            # case with progress variable
            table = PrettyTable()
            table.field_names = ["Workflow number", "Status", 'Progress']
            symbol = {"start": "S", "wait": "W", "end": "F", "error": "E"}
            _string =  [(key, symbol.get(val, '?'), 'NA')
                                for key, val in par_dict.items()]
            main_dir = os.getcwd()
            for ii, keys in enumerate(_string):
                if keys[1] in ['W']:
                    break
                os.chdir(keys[0])
                tmp_db = Database()
                try:
                    progress_var = tmp_db.get_first_loop_val('progress_quantity')
                except KeyError:
                    print("NOTE: progress_quantity not defined")
                    break
                try:
                    tmp_progress = tmp_db.get_current_loop_val(progress_var)
                except KeyError: 
                    # case when progress var not yet added in current loop
                    # we will then instead use the previous loop
                    if tmp_db.get_current_loop_val('loop_count') == 1:
                        break
                    tmp_progress = tmp_db.get_previous_loop_val(progress_var)
                if isinstance(tmp_progress, float):
                    tmp_progress = np.round(tmp_progress,5)
                _string[ii] = (_string[ii][0], _string[ii][1], tmp_progress)
                os.chdir(main_dir)
            table.add_rows(_string)
            status_string.append("S: Submitted, F: Finished, W: Wait, E: Error")
            status_string.append(table)
            return status_string




        def _handle_first_loop(loop, loop_num, keys):
            """ Function rendering the lemmings-hpc status in case of a first loop
                of a chain of a first loop after a --restart
            """
            value_list = []

            for key in keys:
                if key in loop:
                    if key in ['solut_path']:
                        tmp_path = loop[key].split('/')[0]
                        if tmp_path == '.':
                            tmp_path = './'
                        value_list.append(tmp_path)
                    elif key in ['job_id', 'pjob_id']:
                        value_list.append(loop[key])
                    else:
                        value_list.append('Submitted')
                else:
                    value_list.append('Submitted')
            value_list = [str(ii)] + value_list
            
            return value_list
            
        # print()
        # print("Status for chain %s " % (chain_name))
        status_string.append("Status for chain %s " % (chain_name))

        names_keys = keys
        if keys is None:
            # keys = ['solut_path', 'job_id', 'pjob_id', 'dtsum', 'end_cpu_time']
            keys = ['solut_path', 'condition_reached']
            progress_var = 'progress'
            # progress_title = 'progress'
            # progress_scale = 1
            try:
                progress_var = self.get_first_loop_val('progress_quantity')
                # progress_title = self.get_first_loop_val('progress_title')
                # progress_scale = self.get_first_loop_val('progress_scaling_factor')
            except KeyError:
                pass

            keys.append(progress_var)
            keys.extend(['end_cpu_time', 'job_id', 'pjob_id'])

            names_keys = ['Solution path', 'Job end status',
                          'progress', 'CPU time (h)',
                          'job ID', 'pjob ID']

            # if not progress_title == 'progress':
            #     names_keys = [key.replace('progress', progress_title) for key in names_keys]

        end_message = None

        match_cond_reached_keys = {'True': 'ended, finalized',
                                    'False': 'ended, continue',
                                    'None': 'ended, crashed'}
        table = PrettyTable()
        for ii, loop in enumerate(database[chain_name]):
            value_list = []

            # Separate handling of first loop situation
            if self.get_current_loop_val('loop_count') == 1:
                if not 'condition_reached' in loop:
                    # in case condition_reached is present, we went to post_job already
                    # then the handling should be the normal one
                    value_list = _handle_first_loop(loop, ii, keys)
                    table.field_names = ["Loop"] + names_keys
                    table.add_row(value_list)

                    if loop["end_message"] is not None:
                        end_message = customise_end_message(self, ii, loop["end_message"])
                    break

                if not 'end_cpu_time' in loop:
                    # case first loop is running
                    value_list = _handle_first_loop(loop, ii, keys)
                    table.field_names = ["Loop"] + names_keys
                    table.add_row(value_list)
                    break

            if 'restart' in loop:
                if loop['restart']:
                    end_message = None # we reinit the end_message as loop restarted
                    # value_list = ['---']*(len(keys)+1)
                    # table.add_row(value_list)
                    value_list = ['restart'] + ['-----']*len(keys)
                    table.add_row(value_list)
                    value_list = [] # reinit value_list
                    if not 'end_cpu_time' in loop:
                        # for key in keys:
                        #     if key in loop:
                        #         if key in ['solut_path']:
                        #             tmp_path = loop[key].split('/')[0]
                        #             if tmp_path == '.':
                        #                 tmp_path = './'
                        #             value_list.append(tmp_path)
                        #         elif key in ['job_id', 'pjob_id']:
                        #             value_list.append(loop[key])
                        #         else:
                        #             value_list.append('Submitted')
                        #     else:
                        #         value_list.append('Submitted')
                        # value_list = [str(ii)] + value_list
                        value_list = _handle_first_loop(loop, ii, keys)

                        table.field_names = ["Loop"] + names_keys
                        table.add_row(value_list)
                        if loop["end_message"] is not None:
                            end_message = customise_end_message(self, ii, loop["end_message"])
                        break

            if not 'solut_path' in loop and not 'job_id' in loop:
                # JJ: this case won't happen any more I believe
            # print(self.count, ii)
            # if ii == self.count:
                # if 'job_id' in loop:
                #     continue
                if loop["end_message"] is not None:
                    end_message = customise_end_message(self, ii, loop["end_message"])
                break
            else:
                for key in keys:
                    if key in loop:
                        if key in [progress_var]:
                            tmp_key = np.round(loop[key], 4)
                            value_list.append(tmp_key)
                        elif key in ['end_cpu_time']:
                            value_list.append(np.round(loop[key], 3))
                        elif key in ['solut_path']:
                            tmp_path = loop[key].split('/')[0]
                            if tmp_path == '.' and tmp_path is not None:
                                tmp_path = './'
                            value_list.append(tmp_path)
                        elif key in ['condition_reached']:
                            tmp_key = loop[key]
                            value_list.append(match_cond_reached_keys[str(tmp_key)])
                        else:
                            value_list.append(loop[key])
                    else:
                        if 'condition_reached' not in loop: # will only be added in post_job part
                            value_list.append('Submitted')
                        elif key in [progress_var]:
                            value_list.append("NA")
                        elif 'solut_path' not in loop:
                            try:
                                tmp_path = self.get_first_loop_val('solut_path').split('/')[0]
                                if tmp_path == '.' and tmp_path is not None:
                                    tmp_path = './'
                                value_list.append(tmp_path)
                            except KeyError as excep:
                                continue
                        else:
                            value_list.append("NA")
                value_list = [str(ii)] + value_list
                table.field_names = ["Loop"] + names_keys
                table.add_row(value_list)

                # print(loop["end_message"])
                try:
                    if loop["end_message"] is not None:
                        end_message = customise_end_message(self, ii, loop["end_message"])
                except KeyError: # case when post_job still has to run and add end_message to database
                    pass

        status_string.append(table)
        if end_message is not None:
            status_string.append("Lemmings ended: " + end_message)
        
        return status_string

    def safe_access_to_database(self, total_wait = 0, debug = False):
        """ Provide a safe access to performing tasks in a database.
            Idea is to emulate a lock by the combination of access and release
        """
        # Danger is that we end up in endless loop! Need some timeout safety!
        total_wait_max = 100
        if debug:
            total_wait_max = 19
        if total_wait > total_wait_max:
            raise RuntimeError("We waited way too long to access database."
                + "Something is wrong")

        global DATABASE_ACCESSED
        if not DATABASE_ACCESSED:
            DATABASE_ACCESSED = True
            if debug:
                return DATABASE_ACCESSED
        else:
            print("Database is busy: wait 10 s")
            print("Start : %s" % time.ctime())
            time.sleep(10)
            print("End : %s" % time.ctime())
            # raise ValueError("User end")
            self.safe_access_to_database(total_wait= total_wait + 10, debug = debug)


    def release_access_to_database(self):
        """ Function to unlock the access to the database
        """
        global DATABASE_ACCESSED
        DATABASE_ACCESSED = False

def customise_end_message(database, loop_num, end_msg):
    """ Function handling the end message output shown in 'lemmings status'

        Input:
            :database: database class object
            :loop_num: int, number of the loop calling this functionality
        Output:
            :end_message: str, ouput to be provided
    """

    if not isinstance(loop_num, int):
        loop_num = int(loop_num)

    # if not loop_num == 0:
    #     end_message = "\n  Latest loop = %1d \n" % loop_num#(loop_num - 1)
    # else:
    #     end_message = "\n  Latest loop = %1d \n" % loop_num
    end_message = "\n  Latest loop = %1d \n" % loop_num

    try:
        # end_message += ["  Latest job and pjob IDs = "
        #                 + database.get_loop_val('job_id', (loop_num))
        #                 + ' and ' + database.get_loop_val('pjob_id', (loop_num))
        #                 ][0]

        # Starts counting at 1!!
        end_message += ["  Latest job and pjob IDs = "
                        + database.get_loop_val('job_id', (loop_num+1))
                        + ' and ' + database.get_loop_val('pjob_id', (loop_num+1))
                        ][0]
    except KeyError:
        pass

    end_message += '\n  Final status: ' + end_msg
    return end_message


class AbstractLoop:

    # TODO: let's make this abstract

    def __init__(self, condition_reached,
                 job_id=None, pjob_id=None, **kwargs):
        self.condition_reached = condition_reached
        self.job_id = job_id
        self.pjob_id = pjob_id
        self.user_params = kwargs


class Loop(AbstractLoop):

    def __init__(self, solut_path, condition_reached, end_cpu_time,
                 job_id, pjob_id, progress_quantity=None, **kwargs):
        super().__init__(condition_reached, job_id, pjob_id, **kwargs)
        self.solut_path = solut_path
        self.end_cpu_time = end_cpu_time
        self.progress_quantity = progress_quantity


class EndLoop(AbstractLoop):

    def check_sucess(self):
        return self.job_id is not None


class Printer:

    def __init__(self, database):
        self.loops, self.end_loop = self._get_loops(database)

        # create table
        self.table = PrettyTable()
        self.table.field_names = self._get_name_keys()

        # add rows
        for i, loop in enumerate(self.loops):
            info = list(self._get_info(loop))

            self.table.add_row([i] + info)

    def _get_name_keys(self):
        names_keys = ['Loop', 'Solution path', 'Job end status',
                      'progress', 'CPU time (h)',
                      'job ID', 'pjob ID']

        return names_keys

    def _get_loops(self, database):
        chain_name = database.latest_chain_name
        loops = database._database[chain_name]

        loops_ = []
        for i, loop_dict in enumerate(loops):
            if i == 0:
                progress_quantity = loop_dict.get('progress_quantity', None)

            if i == len(loops) - 1:
                Loop_ = EndLoop
            else:
                loop_dict.update({'progress_quantity': progress_quantity})
                Loop_ = Loop

            loops_.append(Loop_(**loop_dict))

        # TODO: check end loop

        return loops_[:-1], loops_[-1]

    def _get_info(self, loop):
        solut_path = self._prettify_solut_path(loop.solut_path)
        condition_reached = self._map_conditioned_reached(loop.condition_reached)
        progress = self._prettify_progress_quantity(loop.user_params.get(loop.progress_quantity, None))
        end_cpu_time = '{:.3f}'.format(loop.end_cpu_time)

        return (solut_path, condition_reached, progress, end_cpu_time,
                loop.job_id, loop.pjob_id)

    def _prettify_solut_path(self, solut_path):
        tmp_path = solut_path.split(os.path.sep)[0]

        # if only `.` makes it prettier
        if tmp_path == '.':
            tmp_path = f'.{os.path.sep}'

        return tmp_path

    def _map_conditioned_reached(self, condition_reached):
        mapping = {True: 'ended, finalized',
                   False: 'ended, continue',
                   None: 'ended, crashed'}

        return mapping[condition_reached]

    def _prettify_progress_quantity(self, progress_value):
        if progress_value is None:
            return 'N/A'

        if type(progress_value) is int:
            return f'{progress_value}'

        # float
        return '{:.4f}'.format(progress_value)

    def print(self):
        print(self.table)
