from sys import platform
import sys
import yaml
import json
import os
import socket as sc
import time

from datetime import datetime, timedelta
from socket import socket

from subprocess import call, Popen, PIPE
from io import StringIO


class Middleware:
    '''
    Manages dependencies for 'phobos cli'

    1. gcloud       check installation, install, auth, set-project, import datalab credentials.
    2. kubectl      check installation, install, switch context, update datalab credentials.
    3. polyaxon     port-forward for local/datalab, close-port-forward.
    4. setup        ready-check, install missing dependencies.
    5. exec         PIPE, sys.std(out/in/err) support with wait and comminicatate support.
    '''
    def __init__(self):
        '''
        Initializes setup_list for installation and ready-check order,
        Initializes .phobos in home directory

        '''
        self.setup_list = ['gcloud','kubectl','gcloud-auth','datalab-credentials']
        self.setup = {
            'gcloud': {
                'check': self.gcloud_check,
                'set': self.gcloud_install,
                'state': False
            },
            'kubectl': {
                'check': self.kubectl_check,
                'set': self.kubectl_install,
                'state': False
            },
            'gcloud-auth': {
                'check': self.gcloud_auth_check,
                'set': self.gcloud_auth_login,
                'state': False
            },
            'datalab-credentials': {
                'check': self.datalab_config_check,
                'set': self.datalab_config_set,
                'state': False
            }
        }
        self.cluster_name = 'gke_granular-ai_us-central1-c_science-lab'
        self.path = os.path.join(os.path.expanduser('~'),'.phobos')
        self.expiry = None
        self.local_port = 31833
        self.datalab_port = 8000

    def exec(self,command,forward=False,pipe=True,in_=""):
        '''
        Popen support with input,out and error support 
        
        Params:
        ---
        command: string     Command to execute.
        forward: bool       Doen't wait for command to complete.
        pipe: bool          If True runs command in backend, else truns command interactively.     
        in_: string         Stdin for PIPEd process call.
        '''
        if pipe:
            stdout, stdin, stderr = PIPE,PIPE,PIPE
        else:
            stdout = sys.stdout
            stdin = sys.stdin
            stderr = sys.stderr
        while True:
            p = Popen(command,shell=True,stdout=stdout,stderr=stderr,stdin=stdin)
            out, err = "",""
            if not pipe:
                p.wait()
                return out,err
            if len(in_) > 0:
                out,err = p.communicate(input=in_.encode('utf-8'))
                out,err = out.decode('utf-8'), err.decode('utf-8')
                if "pip install" in out.lower():
                    continue
                return out,err
            if not forward and len(in_) == 0:
                p.wait()
                out,err = p.stdout.read().decode('utf-8'),p.stderr.read().decode('utf-8')
                return out,err
            else:
                time.sleep(1)
                return "",""
    
    def gcloud_check(self):
        '''
        Check if gcloud is present
        '''
        out,err = self.exec("which gcloud")
        if len(out) < 3 or "not found" in out:
            return False
        return True

    def gcloud_install(self):
        '''
        Provide link to install gcloud
        '''
        print("Kindly follow the steps from here: https://cloud.google.com/sdk/docs/install to install gcloud")
        return

    def kubectl_check(self):
        '''check if kubectl is prosent'''
        out,err = self.exec("which kubectl")
        if len(out) < 3 or "not found" in out:
            return False
        return True

    def kubectl_install(self):
        '''Installs kubectl'''
        if not self.gcloud_check():
            self.request_setup()
            return
        out,err = self.exec("gcloud components install kubectl kubectl-oidc",pipe=False)
        return

    def gcloud_auth_check(self):
        '''Checks gcloud auth @granular.ai'''
        out,err = self.exec("gcloud auth list")
        for out_ in out.split('\n'):
            if '@granular.ai' in out_:
                if '*' in out_:
                    out,err = self.exec('gcloud config get-value project')
                    if 'granular-ai' not in out:
                        out,err = self.exec('gcloud config set project granular-ai')
                        print('Project ID set to "granular-ai"')
                    return True
                else:
                    print("granular.ai id present but not activated !")
                    return False
        return False

    def gcloud_auth_login(self):
        '''log-in to gcloud using granular-id'''
        if not self.gcloud_check():
            self.request_setup()
            return
        out,err = self.exec("gcloud auth list")
        out = out.split('\n')
        out = list(filter(lambda x : 'granular.ai' in x, out))
        if len(out) == 0:
            out,err = self.exec('gcloud auth login',pipe=False)
            print(out)
        elif '*' not in out[0]:
            email = list(filter(lambda x : '@granular.ai' in x, out[0].split(' ')))[0]
            exec(f"gcloud config get account {email}")
        return

    def kubectl_switch_context(self,mode):
        '''switch kubectl context using mode=(datalab/local'''
        if not self.kubectl_check() or not self.datalab_config_check():
            self.request_setup()
            return
        if mode == 'local':
            out,err = self.exec("kubectl config get-contexts")
            if "minikube" not in out:
                print("minikube context not found in KUBECONFIG")
                return False
            out,err = self.exec("kubectl config use-context minikube")
        else:
            out,err = self.exec("kubectl config view")
            if self.cluster_name not in out:
                return False
            out,err = self.exec(f"kubectl config use-context {self.cluster_name}")
        if "switched to context" in out.lower():
            return True
        else:
            return False
    
    def datalab_config_check(self):
        '''Checks if datalab credentials are present and validates credential's expiry date'''
        out,err = self.exec("kubectl config view")
        if self.cluster_name not in out:
            return False
        config_ = yaml.safe_load(out)
        if len(list(filter(lambda x : self.cluster_name in x['context']['cluster'], config_['contexts']))) == 0:
            return False
        user = list(filter(lambda x : self.cluster_name in x['name'],config_['users']))
        if len(user) == 0:
            return False
        user = user[0]
        try:
            exp_date = datetime.strptime(user['user']['auth-provider']['config']['expiry'],"%Y-%m-%dT%H:%M:%SZ")
            diff = exp_date - datetime.now()
            diff = diff.total_seconds()/3600
            if diff < 10:
                False
            if self.expiry is None:
                self.expiry = exp_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            return True
        except:
            return False

    def datalab_config_set(self):
        '''Imports new datalab credentials'''
        if not self.kubectl_check():
            self.request_setup()
            return
        out,err = self.exec("gcloud container clusters get-credentials science-lab --zone us-central1-c --project granular-ai")
        return

    def polyaxon_forward_check(self,mode):
        '''Checks if port corresponding to mode is occupied or not'''
        if not self.datalab_config_check():
            self.request_setup()
            return
        socket_ = socket(sc.AF_INET, sc.SOCK_STREAM)
        port = self.local_port if mode == 'local' else self.datalab_port
        out = socket_.connect_ex(('127.0.0.1',port))
        if out == 0:
            socket_.close()
            return True
        else:
            socket_.close()
            return False

    def close_port(self,mode):
        '''Kills process on port corresponding to mode'''
        if mode == "local":
            self.exec(f"kill -9 $(lsof -i TCP:{self.local_port} | grep LISTEN | awk '{{print $2}}')")
        else:
            self.exec(f"kill -9 $(lsof -i TCP:{self.datalab_port} | grep LISTEN | awk '{{print $2}}')")

    def polyaxon_forward(self,mode):
        '''polyaxon-port forward depending on mode=datalab/local. Kills process running on required port'''
        if mode == "local":
            if not self.polyaxon_forward_check(mode):
                self.close_port(mode)
            if not self.kubectl_switch_context(mode):
                raise Exception("Unable to switch kubectl context, Try manually!")
            out,err = self.exec("polyaxon port-forward -t minikube &", forward=True)
            if len(err) == 0:
                pass
            else:
                raise Exception(f"Error in occupying {self.local_port}")
        else:
            if not self.datalab_config_check():
                self.request_setup()
                return
            if not self.polyaxon_forward_check(mode):
                self.close_port(mode)
            if not self.kubectl_switch_context(mode):
                raise Exception("Unable to switch kubectl context, Try manually!")
            out,err = self.exec("polyaxon port-forward &", forward=True)
            if len(err) == 0:
                pass
            else:
                raise Exception(f"Error in occupying port {self.datalab_port}")

    def project_check(self,project_name,mode):
        '''
        Check if Project with provided project_id present on polyaxon, mode=datalab/local.
        If project is present but is not active, Sets the projcet as active.
        
        '''
        self.polyaxon_forward(mode)
        out,err = self.exec(f"polyaxon project get -p {project_name}",in_='N')
        if "status: 404" in out.lower():
            return False
        else:
            return True

    def project_set(self,project_name,description,tags,mode):
        '''Creates project with provided name, description and tags'''
        self.polyaxon_forward(mode)
        if self.project_check(project_name,mode):
            print(f"Project {project_name} already present")
            return
        out, err = self.exec(f"polyaxon project create --name {project_name} --description={description} --tags={tags}",in_='N')
        out = (out+"\n"+err).lower()
        if "error message" in out:
            return False
        elif "created successfully" in out:
            print(out)
            return True
        else:
            print(out)
            return False

    def run_tensorboard(self,*uuid,project_name=''):
        '''Runs tensorboard integration to polyaxon'''
        if not self.polyaxon_forward_check():
            self.port_forward()
        if len(project_name) > 0:
            if not self.polyaxon_forward_check():
                self.request_setup()
                return
            out,err = self.exec(f"polyaxon run --hub tensorboard -p {project_name}")
        elif len(uuid) == 1:
            out,err = self.exec(f"polyaxon run --hub tensorbaord:multi-run -P {','.join(uuid)}")
        else:
            out,err = self.exec(f"polyaxon tun --hub tensorboard -P {uuid}")
        if len(err) > 0:
            raise Exception('Kindly provide valid arguments')

    def setup_failed(self):
        '''Raises setup failed exception'''
        raise Exception('Setup Failed, Retry again!')

    def setup_install(self,till=""):
        '''Installs missing dependencies'''
        flag = False
        for setup_name in self.setup_list:
            if len(till) > 0 and setup_name == till:
                return True
            print(setup_name)
            if not self.setup[setup_name]['check']():
                install = input(f"Setup {setup_name} ? (yes/no) [yes]").lower()
                if install == '' or install == 'yes':
                    self.setup[setup_name]['set']()
                    if not self.setup[setup_name]['check']():
                        return False
                else:
                    return False
            if flag:
                break
        
        return True
            
    def setup_ready(self,till=""):
        '''Checks if all dependencies are installed and ready.short-circuit the checks based on their order'''
        flag = False
        for setup_name in self.setup_list:
            if len(till) > 0 and setup_name == till:
                flag = True
            if not self.setup[setup_name]['check']():
                return False
            self.setup[setup_name]['state'] = True
            if flag:
                break
        return True

    def dependency_ready(self,dep_name):
        '''Chekcs if specified dependency is ready or not'''
        setup = self.setup[dep_name]
        if not self.setup[setup]['check']():
            return False
        return True

    def request_setup(self, till=""):
        '''Asks user to run setup and install missing dependencies'''
        if not self.setup_ready(till):
            out = input("Dependencies missing, procees to setup ? (yes/no) [yes]").lower()
            if out == "yes" or out == "":
                self.setup_install(till)
                if not self.setup_ready(till):
                    self.setup_failed()
            else:
                self.setup_failed()
