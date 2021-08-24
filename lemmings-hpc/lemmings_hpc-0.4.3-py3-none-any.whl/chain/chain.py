"""
This script executes the fundamentals functions of lemmings workflows.
"""
import sys
import os
import traceback
import shutil
import subprocess
#import logging
#import yaml
from prettytable import PrettyTable
from nob import Nob
import numpy as np

from lemmings_hpc.chain.database import Database
from lemmings_hpc.chain.lemmingjob_base import LemmingsStop

class Lemmings():
    """
    The mother class of Lemmings.
    """
    def __init__(self,
                 lemmings_job):
        """
        :param lemmings_job: An Object that contains all actions/
                             made in the different classical lemmings function:
                             --> function that check conditon(s)
                             --> function that do some actions before update status
                            For example, function "start_to_spawn_job()" can save a file, a fig ...
        """
        self.lemmings_job = lemmings_job
        self.database = Database()


    def run(self):
        """*Submit the chain of computations.*"""

        chain_name = self.lemmings_job.machine.job_name
        if not os.path.exists(chain_name):
            os.mkdir(chain_name)

        # logging.basicConfig(filename="lemmings.log", level=logging.INFO, format='%(message)s')

        # if self.lemmings_job.status == "start":
        #     logging.info("~~~~~~ START NEW Lemmings Chain ~~~~~~~\n")
        # else:
        #     logging.info("\n####### START NEW Lemmings loop #######")

        while self.lemmings_job.status != "exit":
            self.next()
        # else:
        #     print("Lemmings stopped: ", self.lemmings_job.end_message)
                # Could do print: Lemmings status = "started, aborted etc"
                # and in init of end_message = "Starting"
                # the other prints seem to be in log file instead ..
                # so do smth in the CLI? perhaps better to do so?


    def next(self):
        """
        Execute all necessary functions depending on its status
        There are 2 kind of function:
            - Functions that check some conditions
            - Functions that pass from a status to another
    ::

                     - - - > spawn_job < - - -
                    |             |             |
                    |             |             |
                  start             - - - - > post_job
            <check_condition>             <check_condition>
                    |                           |
                    |                           |
                    |                           |
                     - - - - - > Exit < - - - -
        """
        if self.lemmings_job.status == "start":
            _perform_lemmings_job_start(self)

        elif self.lemmings_job.status == "spawn_job":
            _perform_lemmings_job_spawn(self)

        elif self.lemmings_job.status == "post_job":
            _perform_lemmings_job_post(self)


    def _check_cpu_cost(self):
        """Check if the CPU limit is reached."""

        #--testing--#
        last_job_id = self.database.get_current_loop_val('job_id')
        last_cpu_time = self.database.get_current_loop_val('start_cpu_time')


        # last_job_id = self.database.get_previous_loop_val('job_id')
        # last_cpu_time = self.database.get_previous_loop_val('start_cpu_time')

        new_cpu_time = self.lemmings_job.machine.get_cpu_cost(last_job_id)
        total_cpu_time = last_cpu_time + new_cpu_time

        # self.database.update_previous_loop('end_cpu_time',
        #                                    total_cpu_time)
        # self.database.update_current_loop('start_cpu_time',
        #                                   total_cpu_time)
       
        self.database.update_current_loop('end_cpu_time',
                                           total_cpu_time)
        #start cpu time should be updated if new loop!
        #--end testing--#

        if total_cpu_time > self.lemmings_job.cpu_limit:
            self.database.update_previous_loop('cpu_reached',
                                               True)
            self.lemmings_job.status = 'exit'
            self.lemmings_job.end_message = "CPU condition reached"

            self.database.update_current_loop('end_message',
                                    self.lemmings_job.end_message)

            return True
        return False


    def _create_batch(self, batch_j="./batch_job", batch_pj="./batch_pjob"):
        """
        Create the batch that will launch the job and postjob loop of lemmings.
        The construction is based on namedtuple that are unique for each machine.
        So the user, if not already done, have to set up those namedtuple for his machine(cluster).
        """

        # The user can take control of this step which can be done through the
        # expert_params object in the workflow's .yml file
        if hasattr(self.lemmings_job.machine.user, 'expert_params'):
            if 'user_batch' in self.lemmings_job.machine.user.expert_params:
                if self.lemmings_job.machine.user.expert_params['user_batch']:
                    return

        batch_job = self.lemmings_job.machine.job_template.batch
        batch_pjob = (self.lemmings_job.machine.pj_template.batch + '\n'
                      + "lemmings-hpc run "
                      + str(self.lemmings_job.workflow)
                      + " -s post_job"
                      + " --yaml=" + self.lemmings_job.machine.path_yml
                      + '\n')

        with open(batch_j, 'w') as fout:
            fout.write(batch_job)
        with open(batch_pj, 'w') as fout:
            fout.write(batch_pjob)


    def write_log_file(self, usefull_keys=None):
        """write the log file"""
        chain_name = self.database.latest_chain_name
        database = self.database._database
        table = PrettyTable()

        if usefull_keys is None:
            usefull_keys = ['datetime', 'job_id', 'pjob_id', 'dtsum', 'end_cpu_time']

        if chain_name is None:
            raise ValueError("No chain found. Check database file in your current directory ...")
        else:
            log_msg = "Lemmings Version : " + str(database[chain_name][0]['lemmings_version']) + '\n\n'

            for i, loop in enumerate(database[chain_name]):
                value_list = []
                for key in usefull_keys:
                    if key in loop:
                        value_list.append(loop[key])
                    else:
                        value_list.append(None)
                value_list = [str(i)] + value_list
                table.field_names = ["Loop"] + usefull_keys
                table.add_row(value_list)
            log_msg += str(table)
            log_msg += "\n\n"

        if database[chain_name][-1]['safe_stop'] is True:
            log_msg += "Lemmings STOP because using 'safe stop' command\n"
        if 'run_crash' in database[chain_name][-2] and database[chain_name][-2]['run_crash'] is True:
            log_msg += "Your run CRASHED, see avbp.o file\n"
        elif 'condition_reached' in database[chain_name][-2] and database[chain_name][-2]['condition_reached']:
            if 'simu_end_time' in database[chain_name][0]:
                log_msg += ("Condition " + str(database[chain_name][0]['simu_end_time'])
                            + " [s] is     REACHED")

        with open(os.path.join(chain_name, chain_name + '.log'), 'w') as fout:
            fout.write(log_msg)


    def create_replicate_workflows(self):
        """ Method that controls the generation of multiple workflows for parallel mode 
            and submits them according to user settings

             Split in smaller functions
                1) check if all is well activated in workflow.yml
                    -> _check_correct_parallel_settings()
                2) perform the workflow copies
                    -> _generate_workflow_replicates
                3) launch workflows
                    3.1) check if max parallel workflow specied
                    3.2) launch workflows
                    3.3) update the database
                    -> _launch_workflows_parallel
                4) raise LemmingsStop as we did what we had to do at this point
        """

        #Check if parameters correctly defined by user in .yml file
        num_workflows = _check_correct_parallel_settings(self.lemmings_job)

        print("Parallel mode enabled")
        self.database.add_nested_level_to_loop('parallel_runs')

        # Generation of different workflow folder replicates
        workflows_list = _generate_workflow_replicates(num_workflows, self.lemmings_job, self.database)
        # Launch workflows from respective folders
        max_par_wf = _launch_workflows_parallel(workflows_list, self.lemmings_job, self.database)


        try:
            raise LemmingsStop("Replicate workflows launched according to,"
                                + " max parallel chains = %3d " % max_par_wf)
        except TypeError:
            raise LemmingsStop("All replicate workflows launched")


def _perform_lemmings_job_start(lemmings):
    """ Function controls the call sequence associated with the 'start' part of lemmings

        Input:
            :lemmings: Lemmings object

        Output:
            :None
    """

    try:
        start_chain = lemmings.lemmings_job.check_on_start()
        if start_chain:
            lemmings.lemmings_job.prior_to_job()
            lemmings._create_batch()
            lemmings.lemmings_job.status = "spawn_job"
        else:
            lemmings.lemmings_job.abort_on_start()
            lemmings.lemmings_job.status = "exit"
    except LemmingsStop as stop:
        _handle_exception(lemmings.lemmings_job, lemmings.database,
                            stop, lemmings_stop = True)
        lemmings.lemmings_job.status = "exit" #-> can probably remove, to check
    except Exception as any_other_exception:
        _handle_exception(lemmings.lemmings_job,lemmings.database,
                            any_other_exception, lemmings_stop = False)


def _perform_lemmings_job_spawn(lemmings):
    """ Function controls the call sequence associated with the 'spawn_job' part of lemmings

        Input:
            :lemmings: Lemmings object

        Output:
            :None
    """

    try:
        # Defined as one of the methods
        lemmings.lemmings_job.prepare_run()
        safe_stop = lemmings.database.get_previous_loop_val('safe_stop')
    except LemmingsStop as stop:
        _handle_exception(lemmings.lemmings_job,lemmings.database,
                            stop, lemmings_stop= True)
        safe_stop = True
    except Exception as any_other_exception:
        _handle_exception(lemmings.lemmings_job,lemmings.database,
                            any_other_exception, lemmings_stop= False)
        safe_stop = True
    
    if safe_stop is False:
        submit_path = lemmings.database.get_current_loop_val('submit_path')
        try:
            job_id = lemmings.lemmings_job.machine.submit(batch_name="batch_job",
                                                    submit_path=submit_path)
        except FileNotFoundError as excep:
            print("LemmingsError:", excep)
            #TODO: pass through _handle_exception in here
            #       and raise LemmingsStop
            sys.exit()
        try:
            pjob_id = lemmings.lemmings_job.machine.submit(batch_name="batch_pjob",
                                                    dependency=job_id,
                                                    submit_path="./")
        except FileNotFoundError as excep:
            print("LemmingsError:", excep)
            #TODO: pass through _handle_exception in here
            #       and raise LemmingsStop
            sys.exit()

        lemmings.database.update_current_loop('job_id',
                                        job_id)
        lemmings.database.update_current_loop('pjob_id',
                                        pjob_id)
    else:
        lemmings.database.update_current_loop('safe_stop',
                                        True)
    lemmings.lemmings_job.status = "exit"


def _perform_lemmings_job_post(lemmings):
    """ Function controls the call sequence associated with the 'post_job' part of lemmings

        Input:
            :lemmings: Lemmings object

        Output:
            :None
    """

    # A lemmings run is finished if
    #       1) the CPU limit is reached
    #       2) the target condition is reached (e.g. simulation end time)
    #       3) the simulation crashed for some reason
    # condition_reached can take 3 values:
    #       - False: we continue lemmings
    #       - True: target reached, we stop lemmings
    #       - None: crash, we stop lemmings


    # 1) check if cpu cost reached
    condition_reached = lemmings._check_cpu_cost()
    # 2) check if target condition reached 3) or crash
    if not condition_reached:
        try:
            condition_reached = lemmings.lemmings_job.check_on_end()

            if condition_reached is True or condition_reached is None:
                #--testing------#
                # lemmings.database.update_previous_loop('condition_reached',
                #                                 condition_reached)
                 #--end testing--#
                lemmings.database.update_current_loop('condition_reached',
                                                condition_reached)                      
                if condition_reached is None:
                    lemmings.lemmings_job.end_message = "Run crashed"
                else:
                    lemmings.lemmings_job.end_message = "Target condition reached"

                lemmings.database.update_current_loop('end_message',
                            lemmings.lemmings_job.end_message)

                lemmings.lemmings_job.after_end_job()
                _check_and_activate_parallel_mode(lemmings.lemmings_job, "monitor")
                lemmings.write_log_file()
                lemmings.lemmings_job.status = "exit"
            else:
                # lemmings.database.update_previous_loop('condition_reached',
                #                             condition_reached)

                #--testing------#
                lemmings.database.update_current_loop('condition_reached',
                                                 condition_reached)
                lemmings.database.initialise_new_loop()
                lemmings.lemmings_job.loop_count += 1 # increment loop count by 1 as we'll start a new spawn job
                lemmings.database.update_current_loop('loop_count',
                                            lemmings.lemmings_job.loop_count)
                lemmings.database.update_current_loop('end_message',
                                                        None)
                lemmings.database.update_current_loop('start_cpu_time',
                                           lemmings.database.get_previous_loop_val('end_cpu_time'))
                #--end testing--#

                lemmings.lemmings_job.prior_to_new_iteration()
                lemmings._create_batch()
                lemmings.lemmings_job.status = "spawn_job"

        except LemmingsStop as stop:
            _handle_exception(lemmings.lemmings_job,lemmings.database,
                                stop, lemmings_stop= True)
        except Exception as any_other_exception:
            _handle_exception(lemmings.lemmings_job,lemmings.database,
                                any_other_exception, lemmings_stop= False)
    else:
        try:
            # check_on_end required if user does database updates in it
            # also check if user condition is reached and update database param
            condition_reached = lemmings.lemmings_job.check_on_end()
            #--testing------#
            # lemmings.database.update_previous_loop('condition_reached',
            #                                 condition_reached)
            #--end testing--#
            lemmings.database.update_current_loop('condition_reached',
                                                condition_reached)
            lemmings.lemmings_job.end_message = "Target CPU limit reached"
            lemmings.database.update_current_loop('end_message',
                            lemmings.lemmings_job.end_message)
            lemmings.lemmings_job.after_end_job()
            _check_and_activate_parallel_mode(lemmings.lemmings_job, "monitor")
            lemmings.write_log_file()


            lemmings.lemmings_job.status = "exit"
        except LemmingsStop as stop:
            _handle_exception(lemmings.lemmings_job,lemmings.database,
                                stop, lemmings_stop= True)
        except Exception as any_other_exception:
            _handle_exception(lemmings.lemmings_job,lemmings.database,
                                any_other_exception, lemmings_stop= False)

def _check_correct_parallel_settings(lemmings_job):
    """ Controlling whether everything correctly set by user for 'farming' mode of lemmings

        Input:
            :lemmings_job: lemmings job object

        Output:
            :num_workflow: int, number of separate workflows to consider
    """

    try:
        if not 'parallel_mode' in lemmings_job.machine.user.expert_params:
            raise KeyError
        if lemmings_job.machine.user.expert_params["parallel_mode"] is not True:
            raise ValueError
    except ValueError as excep:
        raise LemmingsStop("Parallel mode not activated, please do so through\n"
            + "expert_params:\n"
            + "  parallel_mode: True\n"
            + "\n"
            + "in the workflow.yml")
    except KeyError as excep:
        raise LemmingsStop("Parallel mode key not specified, please do so through\n"
            + "expert_params:\n"
            + "  parallel_mode: True\n"
            + "\n"
            + "in your workflow.yml")

    try:
        num_workflows = len(lemmings_job.machine.user.parallel_params['parameter_array'])
    except KeyError:
        raise LemmingsStop("parameter array not or wrongly specified, please use this structure:\n"
                        + "parallel_params:\n"
                        + "  parameter_array: \n"
                        + "  - par1: value \n"
                        + "    par2: value \n"
                        + "  - par1: value \n"
                        + "    par3: value \n"
                        + "  - par2: value \n"
                        + "    par4: value \n"
                        + "\n"
                        + "in your {workflow}.yml")

    return num_workflows

def _generate_workflow_replicates(workflow_nbs, lemmings_job, database):
    """ Function performing the actual replication of the current work folder structure
        for separate lemmings calls

        Input:
            :workflow_nbs: int, number of copies to create
            :lemmings_job: lemmings_job object
            :database:    Database object  

        Output:
            :workflows_list: list of type string containing workflow folders generated
    """

    workflows_list = []

    dir_info = os.listdir()
    for ii in np.arange(workflow_nbs):
        tmp_workflow = "WF_%03d" %ii
        # In case the user specified a name for his workflow
        try:
            tmp_workflow += ("_"+
                lemmings_job.machine.user.parallel_params['parameter_array'][ii]["workflow_name"])
        except KeyError as excep:   
            pass

        try:
            if os.path.isdir(tmp_workflow) and lemmings_job.machine.user.parallel_params["overwrite_dirs"]:
                shutil.rmtree(tmp_workflow)
            os.mkdir(tmp_workflow)
        except KeyError:
            raise LemmingsStop("Overwrite directory option not specified, please do so through\n"
                            + "parallel_params:\n"
                            + "  overwrite_dirs: True or False\n"
                            + "\n"
                            + "in the workflow.yml")
        except FileExistsError as excep:
            _handle_exception(lemmings_job,database,
                                    excep, lemmings_stop= False)
            sys.exit()

        for item in dir_info:
            if os.path.isfile(item):
                if item not in [database.db_path.split("./")[-1],
                                    lemmings_job.workflow+".yml"]:
                    shutil.copy(item, tmp_workflow)
            else:
                if item not in [database.latest_chain_name]:
                    if item.split('_')[0] != "Workflow" and item not in database.get_chain_names():
                        lemmings_job.pathtools.copy_dir(item, tmp_workflow+"/")

        workflows_list.append(tmp_workflow)
        
    return workflows_list

def _launch_workflows_parallel(workflows_list, lemmings_job, database):
    """ Function performing the actual replication of the current work folder structure
        for separate lemmings calls

        Input:
            :workflow_list: list of type string containing names of workflows to consider
            :lemmings_job: lemmings_job object
            :database:    Database object  

        Output:
            :max_par_wf: None or int with number of max nb of simultaneous workflows to launch
    """

    tmp_path = os.getcwd()
    for ii, workflow in enumerate(workflows_list):
        # go to subdirectory to launch lemmings
        os.chdir(workflow)

        max_par_wf = None
        try:
            max_par_wf = lemmings_job.machine.user.parallel_params["max_parallel_workflows"]
            if not ii+1 > max_par_wf:
                subprocess.call("lemmings-hpc run " + lemmings_job.workflow + " --noverif"
                                + " --yaml=../"+lemmings_job.workflow+".yml" , shell = True)
            # go back to main directory
            os.chdir(tmp_path)
            if not ii+1 > max_par_wf:
                database.update_nested_level_to_loop('parallel_runs',workflow, 'start')
            else:
                # case in which we put them on hold for submission at later stage
                database.update_nested_level_to_loop('parallel_runs',workflow, 'wait')
        except KeyError:
            subprocess.call("lemmings-hpc run " + lemmings_job.workflow + " --noverif"
                            + " --yaml=../"+lemmings_job.workflow+".yml" , shell = True)
            os.chdir(tmp_path)
            database.update_nested_level_to_loop('parallel_runs',workflow, 'start')
        except TypeError:
            subprocess.call("lemmings-hpc run " + lemmings_job.workflow + " --noverif"
                            + " --yaml=../"+lemmings_job.workflow+".yml" , shell = True)
            os.chdir(tmp_path)
            database.update_nested_level_to_loop('parallel_runs',workflow, 'start')

    return max_par_wf

def _handle_exception(lemmings_job, database, exception, lemmings_stop = False):
    """ Function that performs the updates in case an exception is raised through
        LemmingsStop or other

        Input:
            lemmings_job: lemmings_job class object
            database: database class object
            exception: raised exception class message
            lemmings_stop: boolean, whether exception raised through LemmingsStop or not
        Output:
            None: performs updates in database and ends the lemmings chain
    """

    end_msg = str(exception)
    if not lemmings_stop:
        end_msg = "Unexpected exception: " + end_msg + "\n" + traceback.format_exc()
        traceback.print_exc()

    lemmings_job.end_message = end_msg
    database.update_current_loop("end_message", lemmings_job.end_message)
    lemmings_job.status = "exit"


def _check_and_activate_parallel_mode(lemmings_job, stage):
    """ Function that checks if the parallel mode has been activated and acts
        accordingly

        Input:
            lemmings_job: lemmings_job class object
            stage: str, which parallel functionality to call
                    = create: create_replicate_workflows()
                    = monitor: monitor_replicate_workflows()

        Output:
            None: launches parallel mode functions if parallel mode activated
    """

    if hasattr(lemmings_job.machine.user, 'expert_params'):
        if 'parallel_mode' in lemmings_job.machine.user.expert_params:
            if lemmings_job.machine.user.expert_params['parallel_mode']:
                if stage == "create": # moved call to cli.py
                    lemmings_job.create_replicate_workflows()
                elif stage == "monitor":
                    lemmings_job.monitor_replicate_workflows()
                else:
                    raise LemmingsStop("Unknown parallel stage function")


    # def write_log_file(self):
    #     """write the log file"""
    #     chain_name = self.database.latest_chain_name
    #     database = self.database._database

    #     usefull_keys = ['datetime', 'job_id', 'pjob_id', 'init_path', 'temporal_path', 'dtsum']
    #     columns_len = [20, 30]

    #     if chain_name is None:
    #         print("No chain found. Check database file in your current directory...")
    #     else:
    #         log_msg = ("\n#########################################\n"
    #                    + "         # Lemmings Version : "
    #                    + str(database[chain_name][0]['lemmings_version']) + " #         \n"
    #                    + "#########################################\n\n")


    #         for i, loop in enumerate(database[chain_name]):
    #             log_msg += "\n\n"
    #             log_msg += self.write_head(columns_len, i+1)

    #             for key in loop:
    #                 if key in usefull_keys:
    #                     key_blank_nb = self.adjust_column_size(key, size=20)
    #                     val_blank_nb = self.adjust_column_size(loop[key], size=30)
    #                     log_msg += ('|' + str(key) + key_blank_nb * " "
    #                                 + str(loop[key]) + val_blank_nb * " " + '|' + '\n')

    #                     log_msg += "├" + (sum(columns_len)) * " " + "┤"  + '\n'

    #             log_msg += "├" + (sum(columns_len)) * "-" + "┤"

    #         log_msg += "\n\n"
    #         log_msg += self.write_whole_chain_param(database, chain_name)

    #     with open(os.path.join(chain_name, chain_name + '.log'), 'w') as fout:
    #         fout.write(log_msg)


    # def adjust_column_size(self, key, size):

    #     word_len = len(str(key))
    #     return(size - word_len)

    # def write_head(self, columns_len, loop_nb):
    #     tot_size = sum(columns_len)
    #     log_msg =  "\n├" + (tot_size) * "-" + "┤" +'\n'

    #     log_msg += ('|' + (int(tot_size/2)-4)* " " + "LOOP N° " + str(loop_nb) + '|'
    #                 + self.adjust_column_size("LOOP N°", int(tot_size/2)) * " " + '\n')
    #     log_msg += "├" + tot_size * '-' + "┤" +'\n'
    #     return log_msg

    # def write_whole_chain_param(self, database, chain_name):

    #     log_msg = ("\n\nTotal physical time [s]   " + str(database[chain_name][-2]['dtsum']) + '\n'
    #                + "Total CPU cost [hours]    " + str(database[chain_name][-2]['end_cpu_time']) + '\n')


    #     if database[chain_name][-1]['safe_stop'] == True:
    #         log_msg += "Lemmings STOP because using 'safe stop' command "
    #     if 'run_crash' in database[chain_name][-2]:
    #         log_msg += "Your run CRASH, see avbp.o file"
    #     if 'condition_reached' in database[chain_name][-2]:
    #         log_msg += ("Condition " + str(database[chain_name][0]['simu_end_time'])
    #                     + " [s] is    REACHED")

    #     return log_msg
