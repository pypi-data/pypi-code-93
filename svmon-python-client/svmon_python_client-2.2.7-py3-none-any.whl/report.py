#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
import subprocess
import sys
import logging
from . import services
from . import json_operations
from svmon_client import remoteConfig
from platform import python_version

try:
    from dotenv import load_dotenv
except ImportError:
    if(python_version() >= '3.0'):
        sys.exit("You need dotenv! install it from http://pypi.python.org/pypi/python-dotenv or run python3 -m pip install python-dotenv.")
    else:
        sys.exit("You need dotenv! install it from http://pypi.python.org/pypi/python-dotenv or run python -m pip install python-dotenv.")

class SVMONReport:

    def __init__(self):
        load_dotenv()
        self.site=""
        self.host=""
        self.service_names=[]
        self.service_type=""
        self.operating_system=""
        self.tags=[]
        self.config = remoteConfig.RemoteConfig().getConfig()
        cwd = os.path.dirname(services.__file__)
        filename = cwd + "/config.json"
        if os.path.exists(filename) == False:
            f=open(filename,'w')
            f.write('{"site": "kit", "service_type":"b2safe", "host":"irods-3-eudat.lsdf.kit.edu"}')
            f.close()
        readok = os.access(filename,os.R_OK)
        if readok == False:
            print("You have no access to read config file: config.json")
            exit(-1)
        with open(filename, 'r') as f:
            load_dict= json.load(f)
            self.site=str(load_dict['site'])
            self.host=str(load_dict['host'])
            self.service_type=str(load_dict['service_type'])


    def refresh_service_name_and_tag(self):
        if services.in_service_list(self.service_type) == False:
            print("service type not configured")

        if self.service_type == "b2access" or self.service_type == "b2drop" or self.service_type == "b2share":
            cwd = os.path.dirname(services.__file__)
            filename = cwd + "/components.json"
            readok = os.access(filename,os.R_OK)
            if readok == False:
                print("You have no access to read config file: components.json")
                exit(-1)
            with open(filename, 'r') as f:
                try:
                    load_dict = json.load(f)
                    if 'components' in load_dict and 'versions' in load_dict:
                        self.set_service_names(load_dict['components'])
                        self.set_tags(load_dict['versions'])

                    if len(self.service_names) != len(self.tags):
                        print("The length of the components is not equal to the versions")
                        exit(-1)

                except ValueError:
                        print("Your components.json file is not valid, please setup your configuration again or contact us for support via svmon --help")
                        exit(-1)

        else:
            self.service_names = services.get_service_name(self.service_type)

            b2handle_config= {}
            if self.service_type == 'b2handle' or self.service_type == "B2HANDLE":
                cwd = os.path.dirname(services.__file__)
                filename = cwd + "/config.json"
                readok = os.access(filename, os.R_OK)
                if readok == False:
                    print("You have no access to config file: config.json")
                    exit(-1)
                with open(filename, 'r') as f:
                    load_dict= json.load(f)
                    if 'handle_server_path' in load_dict:
                        if  load_dict.get('handle_server_path') != None and load_dict.get('handle_server_path') != '':
                            b2handle_config['handle_server_path'] = load_dict.get('handle_server_path')
                        self.tags = services.get_service_tag(self.service_type,b2handle_config)
                    else:
                        print("No configuration for b2handle, please see svmon help")
                        exit(1)
            else:
                self.tags = services.get_service_tag(self.service_type)


    def get_site(self):
        return self.site

    def get_host(self):
        return self.host

    def get_service_names(self):
        return self.service_names

    def get_service_type(self):
        return self.service_type

    def get_tags(self):
        return self.tags

    def set_site(self,site):
        if isinstance(site,str):
            self.site=site

    def set_host(self,host):
        if isinstance(host,str):
            self.host=host

    def set_service_names(self,service_names):
        if isinstance(service_names,list):
            self.service_names=service_names

    def set_service_type(self,service_type):
        if isinstance(service_type,str):
            self.service_type=service_type

    def set_tags(self,tags):
        if isinstance(tags,list):
            self.tags=tags

    def set_operating_system(self,operating_system):
        if isinstance(operating_system,str):
            self.operating_system=operating_system

    def set_service_names_and_tags(self,service_name,tag):
        this.service_names.append(service_name)
        this.tags.append(tag)


    def print_report(self):
        if len(self.service_names) > 0:
            res=[]
            if self.service_names== None or len(self.service_names ) < 1:
                print("no service names is resolved at your host")
                exit(1)
            if  self.tags == None or len(self.tags) < 1:
                print("no service component version is resolved at your host")
                exit(1)
            j=0
            for i in range(len(self.service_names)):
                if j < len(self.tags) and self.tags[j] != None and self.tags[j] != "" :
                    res.append(self.site+'\t'+self.host+'\t'+self.operating_system+'\t'+self.service_type+'\t'+self.service_names[i]+'\t'+self.tags[j]+'\n')
                    j = j +1
                    #print(self.service_names[i])
            return res
        else:
            print("Zero service components")
            return []



    def jsonify(self):
        if len(self.service_names) > 0:
            res = {}
            res['site']= self.site
            res['host'] = self.host
            res['operating_system'] = self.operating_system
            res['service_type'] = self.service_type
            res['service_names'] = self.service_names
            res['tags'] = self.tags
            return res
        else:
            print("No services to be jsonified")
            return {}

    def save_b2handle_config_to_json(self,handle_server_path=None):
        if handle_server_path == None :
            print("No b2handle configuration input")
            exit(-1)
        if handle_server_path != None and isinstance(handle_server_path,str) == False:
            print("Handle server path should be a string")
            exit(-1)
        if  handle_server_path == "":
            print("No input for b2handle configuration")
            exit(-1)

        res={}
        res['site']= self.site
        res['host'] = self.host
        res['service_type'] = self.service_type
        if handle_server_path != "":
            res['handle_server_path'] = handle_server_path


        cwd = os.path.dirname(services.__file__)
        filename = cwd + "/config.json"
        writeok = os.access(filename, os.W_OK)
        if writeok == False:
            print("You have no access to write config file: config.json")
            exit(-1)
        success = json_operations.save_to_file(filename,res)
        if success == False:
            print("Save json data failed")
            exit(1)
        else:
            print("Saved B2HANLE configuration")



    def save_to_json(self):
        if self.site != "" and self.site != None:
            res = {}
            res['site']= self.site
            res['host'] = self.host
            res['service_type'] = self.service_type
            if self.service_type == "b2hanle" or self.service_type == "B2HANDLE":
                cwd = os.path.dirname(services.__file__)
                filename = cwd + "/config.json"
                with open(filename, 'r') as f:
                    load_dict= json.load(f)
                    if 'handle_server_path' in load_dict and load_dict.get('handle_server_path') != None and load_dict.get('handle_server_path') != "":
                        res['handle_server_path'] = load_dict.get('handle_server_path')

            cwd = os.path.dirname(services.__file__)
            filename = cwd + "/config.json"
            if os.path.exists(filename) == False:
                f = open(filename, 'w')
                f.close()
            writeok = os.access(filename, os.W_OK)
            if writeok == False:
                print("You have no access to write config file: config.json")
                exit(-1)
            success = json_operations.save_to_file(filename,res)
            if success == False:
                print("Save json data failed")
                exit(1)
        else:
            print("No services to be jsonified")
            exit(1)



    def save_with_components_to_json(self,specified_components, specified_versions):

        if specified_components== None or specified_versions == None and len(specified_versions) == 0 \
                and len(specified_components) ==0 and len(specified_versions) != len(specified_components):
            print("Please input valid service components and versions to save")
            exit(1)


        cwd = os.path.dirname(services.__file__)
        filename = cwd + "/components.json"
        if os.path.exists(filename) == False:
            f=open(filename,'w')
            f.close()

        writeok = os.access(filename,os.W_OK)
        if writeok == False:
            print("You have no access to write config file: components.json")
            exit(-1)

        res = {}
        res['components'] = specified_components
        res['versions'] = specified_versions

        success = json_operations.save_to_file(filename,res)
        if success == False:
            print("Save component data failed")
            exit(1)
        else:
            print("Successfully saved component data")
            exit(1)




    def set_pair(self,key,value):
        if isinstance(key,str) == False:
            print("Key should be a string")
            exit(1)

        if key == "site":
            self.set_site(value)
        elif key == "host":
            self.set_host(value)
        elif key == "service_type":
            self.set_service_type(value)
        elif key == "operating_system":
            self.set_operating_system(value)
        elif key == "service_names":
            self.set_service_names(value)
        elif key == "tags":
            self.set_tags(value)
        else :
            print("such key is not supporteed: %s\n" %key)
            exit(1)


    def check_site(self):
        return True


    def check_host(self):
        return True

    def print_config_file(self):
        cwd = os.path.dirname(services.__file__)
        filename = cwd + "/config.json"
        with open(filename, 'r') as f:
            load_dict = json.load(f)
            print("The following are your current configurations: ")
            for k, v in load_dict.items():
                print(str(k) +'=  ' +str(v))
            print('Please use svmon --site <SITE> --host <HOST> --type <TYPE> --dump to change your configuration')
            print('More details, please see svmon --help')



    def send_report_to_svmon_server(self):
       import requests as re
       print('Sending report to svmon server...')
       cwd = os.path.dirname(services.__file__)
       apiToken = ""
       filename = os.environ.get('TOKEN_PATH', cwd + "/token.json")
       if os.path.exists(filename) == False:
           print("You have no token configured, please go to svmon.eudat.eu webpage  to create a token and configure it")
           exit(-1)
       readok = os.access(filename, os.R_OK)
       if readok == False:
           print("You have no access to read config file: token.json")
           exit(-1)
       with open(filename, 'r') as f:
           load_dict = json.load(f)
           if 'token' in load_dict and load_dict.get('token') != '':
               apiToken = load_dict.get('token')
           else:
               print("Please configure api token")
               exit(1)

       url = self.config['BACKEND_URL']
       enableDebug = self.config['DEBUG_MODE']
       if(enableDebug):
           print("BACKEND_URL :" + url)

       headers = {}
       headers['Content-Type'] = 'application/json'
       headers['Authorization'] = 'Bearer ' + apiToken

       cert = os.environ.get('CERTIFICATE_PATH', cwd + "/chain_TERENA_SSL_CA_3.pem")
       if(not len(self.service_names)):
           print('No services available, sending report failed')
           exit(1)

       postErrors = 0
       for i in range(len(self.service_names)):
           res = {}
           res['siteName']=self.site
           res['hostNameId']=self.host
           res['operatingSystem']=self.operating_system
           res['serviceType']=self.service_type
           res['serviceComponentName']=self.service_names[i]
           res['tagAtSite']=self.tags[i]
           if(enableDebug):
               print('Going to send report: ',res,' to endpoint: ' + url)
               print('Certificate path: ', cert)
           try:
               if(enableDebug):
                   logging.basicConfig()
                   logging.getLogger().setLevel(logging.DEBUG)
                   requests_log = logging.getLogger("requests.packages.urllib3")
                   requests_log.setLevel(logging.DEBUG)
                   requests_log.propagate = True
               r = re.post(url, data=json.dumps(res), headers=headers, verify=cert)
               #r = re.post(url, headers=headers, data=json.dumps(res), verify=False)
               print('Request to svmon server finished with status code:', r.status_code)
               if(r.status_code == 401):
                   print('Sending report failed, user not authorized, did you provided a valid token?, please check your token.json')
                   exit(1)
               if(r.status_code == 404):
                   print('Service ', self.service_type,' does not exists, please check the svmon config')
                   postErrors +=1
                   continue
               if(r.status_code == 400):
                   print(r.json())
                   postErrors +=1
                   continue
               if (r.status_code != 201 and r.status_code != 200):
                   print('Sending report failed, please check your configuration')
                   exit(1)
           except re.exceptions.RequestException as e:
               print('Sending report failed, host offline?')
               exit(1)
       if(postErrors > 0):
           if(postErrors == len(self.service_names)):
               print('Sending report failed, please check your configuration')
               exit(1)
           print('Sending report finished with some failed reports: ${postErrors}/${len(self.service_names)}, please check your configuration')
           exit(1)
       print('Report has been sent successfully.')
       exit(0)


    def save_token(self,token):
        print('Saving token...')
        if token == "":
            print("No token to be saved")
            exit(0)
        cwd = os.path.dirname(services.__file__)
        filename = cwd + "/token.json"
        res={}
        res['token'] = token
        if os.path.exists(filename) == False:
            f = open(filename, 'w')
            f.close()
        writeok = os.access(filename, os.W_OK)
        if writeok == False:
            print("You have no access to write config file: token.json")
            exit(-1)
        success = json_operations.save_to_file(filename, res)
        if success == False:
            print("Save token data  to json failed")
            exit(1)




if __name__=="__main__":
    re=SVMONReport()
    re.save_to_json()
