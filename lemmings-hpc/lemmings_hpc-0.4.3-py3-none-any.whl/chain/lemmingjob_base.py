""" The lemmings base class containing the methods which get inherited by LemmingJob
"""
import os
import subprocess
import numpy as np
from nob import Nob


from lemmings_hpc.chain.path_tool import PathTools
from lemmings_hpc.chain.database import Database

class LemmingJobBase():

    def __init__(self,
                 workflow,
                 machine,
                 loop_count,
                 status="start",
                 cpu_limit=None,
                 base_dir=None
                 ):

        self.pathtools = PathTools(base_dir)
        self.database = Database()
        self.workflow = workflow
        self.machine = machine
        self.status = status    #start, spawn_job, post_job, exit
        self.cpu_limit = cpu_limit
        self.loop_count = loop_count
        self.end_message = None

        if self.status == 'start':
            self.database.update_current_loop('loop_count',
                                            self.loop_count)
            self.database.update_current_loop('end_message',
                                            self.end_message)

        # can be overruled in expert  params but not for now
        #self.max_parallel_workflows = 2

    """
    A lemming job follows always the same pattern.
    START > SPAWN JOB> POST JOB > SPAWN JOB > POST JOB > EXIT

    each step can be customized in the present class.
    e.g. you control the nb. of SPAWN JOB>POST JOB with the 'Check on end` function.


                 Prior to job  +---------+             Prepare run
                     +--------->SPAWN JOB+---------------------+
                     |         +------^--+                     |
                     |                |                      +-v------+
                   True               |                      |POST JOB|
    +-----+          |                |                      +--------+
    |START+--->Check on start         |                          v
    +-----+          |                +---------------False-Check on end
                   False            Prior to new iteration       +
                     |                                         True
                     |                                           |
                     |                                           |
                     |           +----+                          |
                     +---------->|EXIT|<-------------------------+
               Abort on start    +----+                After end job

    you can use the database if you need to store info from one job to the other.

    The following definition of methods allows a single lemmings run to be performed without any other user input
    except for the required .yml file information.

    """
    def prior_to_job(self):
        """
        Function that prepares the run when the user launches the Lemmings command.
        """

        pass

    def abort_on_start(self):
        """
        What lemmings does if the criterion is reached in the first loop.
        """

        pass

    def prepare_run(self):
        """
        Prepare the run before submission.
        """

        pass

    def prior_to_new_iteration(self):
        """
        Prepare the new loop specific actions if criterion is not reached.
        """

        pass

    def after_end_job(self):
        """
        Actions just before lemmings ends.
        """

        pass


    def check_on_start(self):
        """
        Verify if the condition is already satisfied before launching a lemmings chain.

        Function returns a boolean which starts the chain run. Default set to True.

        A minimum required action is to set the 'start_cpu_time' so that lemmings can check
        if the max cpu condition is reached.

        """

        self.database.update_current_loop('start_cpu_time', 0.)
        start_chain = True

        return start_chain


    def check_on_end(self):
        """
        Verifications after each job loop

         The function check_on_end needs to return a boolean (default True) with three options:
             - False: we continue lemmings
             - True: target reached, we stop lemmings (default setting)
             - None: crash, we stop lemmings

        Default verification by lemmings:
             - is the cpu condition (.yml file) reached?
         """

        condition_reached = True

        return condition_reached

    def monitor_replicate_workflows(self, debug = False):
        """ Function that monitors the number of parallel jobs currently run

            Idea is to update the job status in the main database.yml.
                Status should be either: start, hold, end
                So:
                    1) I must be able to access the main database.yml
                    2) I must be able to submit new lemming jobs
                    3) I must update database status
        """

        wf_dir = os.getcwd() # need ton know where I am to update the main database
        wf_current = wf_dir.split('/')[-1]
        # print("Current workflow", wf_current)

        # absolute path to main directory --> considers a fixed structure!
        base_run_path = "/" + os.path.join(*self.machine.path_yml.split('/')[0:-1])
        os.chdir(base_run_path)
        # print(os.getcwd())
        # Lock access to database
        try:
            self.database.safe_access_to_database(debug = debug)
        except RuntimeError as excep:
            raise LemmingsStop("Monitoring of lemmings chains stopped", excep)
        # Do stuff with our database
        db_info = Nob(self.database._database)
        # Modify status of current workflow: from start to end
        #db_wf_path, = db_info.find(wf_current)
        #print(db_info[db_wf_path][:])
        self.database.update_nested_level_to_loop('parallel_runs',wf_current, 'end')
        db_info = Nob(self.database._database) # required for full status
        #print(db_info[db_wf_path][:]) # doesn't work directly, need to reread it somehow


        # Find next lemmings chain to launch through 'hold' keyword
        status_list = []
        db_subtree = db_info[self.database.latest_chain_name]
        #print(db_subtree)
        for key in db_subtree.parallel_runs[:][0].keys():
            #print(key)
            #print(db_info[key][:])
            if db_subtree[key][:] == 'wait':
                print("We found new job to launch ", key)
                self.database.update_nested_level_to_loop('parallel_runs',key, 'start')
                os.chdir(key)
                if not debug:
                    subprocess.call("lemmings-hpc run " + self.workflow + " --noverif"
                            + " --yaml=../"+self.workflow+".yml" , shell = True)
                os.chdir(base_run_path) # back to main directory
                if debug:
                    self.database.release_access_to_database()
                    os.chdir(wf_dir)
                    return 'Subprocess should have been launched'
                break
            status_list.append(db_subtree[key][:])
            self.database.update_current_loop("end_message", "All lemmings chains"
                                        +  " have been submitted")
        if len(np.unique(status_list)) == 1:
            self.database.update_current_loop("end_message", "All lemmings chains have ended")

        # Release access to database
        self.database.release_access_to_database()
        os.chdir(wf_dir)

class LemmingsStop(Exception):
    """ Definition of a class to allow exit of Lemmings safely upon exceptions
    """

    pass
