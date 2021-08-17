import __main__
import re

def get_version_number():
    path = __main__.os.path.abspath(__main__.os.getcwd())
    # grep 'version\s*=\s*' setup.py  | tr -d 'version=' | tr -d ',' | awk '{print $1}' ## get version in python
    # make provision to get version number from java type project
    process_result = __main__.Popen("node -p \"require('./package.json').version\"", shell=True, stdout=__main__.PIPE, cwd=path)
    version_result = process_result.communicate()[0]
    return str(version_result, 'utf-8')

def setup_variables():
    if __main__.group_id == '':
        __main__.group_id = __main__.os.environ.get('NEXUS_GROUP_ID')   
        if __main__.group_id == '':
            print("Fail to obtain Nexus group id from environment variables")
            return __main__.sys.exit(2)  

    # To-do: Fix artifact name
    if __main__.artifact_name == '':
        __main__.artifact_name = __main__.os.environ.get('CI_PROJECT_NAME')
        # Fix to add extension, right now it is just a folder
        if __main__.artifact_name == '':
            print("Could not obtain project name from git repository to use as artifact name")
            return __main__.sys.exit(2)     
    
    if __main__.repository_name == '':
        __main__.branch_name = __main__.os.environ.get('CI_COMMIT_BRANCH')
        if __main__.branch_name == '':
            print("Could not compute repository name to store to based on branch name e.g <organization>-snapshots")
            return __main__.sys.exit(2)  
        else:
            if 'master' == __main__.branch_name or __main__.branch_name.startswith('release'):
                __main__.repository_name = 'egov-releases'
            elif 'staging' == __main__.branch_name:
                 __main__.repository_name = 'egov-staging'
            elif 'hotfix-deploy' in __main__.branch_name:
                 __main__.repository_name = 'egov-snapshots' 
            else:
                __main__.repository_name = 'egov-snapshots'
            print("INFO: Nexus repository used: ", __main__.repository_name)
                
    if __main__.nexus_format == 'raw' and __main__.directory == '':
        print("RAW nexus repository format requires a directory")
        return __main__.sys.exit(2)
      
    if __main__.nexus_format == 'maven' and __main__.group_id == '':
        print("Maven2 repository requires Group ID  e.g com.<organization>.<applicationname>")
        return __main__.sys.exit(2)
    
    if __main__.username == '':
        __main__.username = __main__.os.environ.get('NEXUS_USERNAME')
        if __main__.username == '' or __main__.username is None:
            print("Fail to retrieve Nexus username from environment variables")
            return __main__.sys.exit(2)
    
    if __main__.password == '':
        __main__.password = __main__.os.environ.get('NEXUS_PASSWORD')
        if __main__.password == '' or __main__.password is None:
            print("Fail to retrieve Nexus password from environment variables")
            return __main__.sys.exit(2)
    
    if __main__.work_directory == '':
        __main__.work_directory = __main__.os.path.abspath(__main__.os.getcwd())
        
    __main__.auth = (__main__.username, __main__.password)    
    
    if 'service/rest' in  __main__.repository_base_url:
        __main__.repository_full_url = __main__.repository_base_url
    else: 
        __main__.repository_full_url = __main__.repository_base_url + "/" + "service/rest/v1/components"
    

def upload_nexus_raw():
    params = (('repository', __main__.repository_name),)
	
    finalpath = __main__.work_directory + '/' + __main__.artifact_name
    print("Uploading to Nexus Repository: "+ __main__.repository_name)
    files = {
        'raw.directory' : (None, __main__.directory),
	    'raw.asset1' : (None, finalpath),
	    'raw.asset1.filename': (None, __main__.artifact_name)
    }
	
    response = __main__.requests.post(url=__main__.repository_full_url, params=params, files=files, proxies=__main__.proxies, auth=__main__.auth)
    if response.status_code == 204:
        print("Nexus Upload successful")
        return __main__.sys.exit(0)
    elif response.status_code == 404:
        print("ERROR: Invalid Nexus URL specified. URL not found.")
        return __main__.sys.exit(1)
    elif response.status_code == 400 and ("release" in __main__.repository_name or "staging" in __main__.repository_name):
        print("Nexus Upload failed. Please modify version number")
        return __main__.sys.exit(1)
    else:
        print("Nexus Upload failed")
        return __main__.sys.exit(1)
    print("Status code: ", response.status_code)

def upload_nexus_npm():
    params = (('repository', __main__.repository_name),)
    finalpath = __main__.work_directory + '/' + __main__.artifact_name
    files = {
	    'npm.asset' : (None, finalpath),
    }
    response = __main__.requests.post(url=__main__.repository_full_url, params=params, files=files, proxies=__main__.proxies, auth=__main__.auth)
    if response.status_code == 204:
        print("Nexus Upload successful")
        return __main__.sys.exit(0)
    else:
        print("Nexus Upload failed")
        return __main__.sys.exit(1)
    print("Status code: ", response.status_code)

def upload_nexus_maven():
    actual_artifact_name = ''
    extension = ''
    versionnumber = ''
    
    path = __main__.os.path.abspath(__main__.os.getcwd())
    
    params = (('repository', __main__.repository_name),)
   
    #finalpath = __main__.work_directory + '/' + __main__.artifact_name
    finalpath = __main__.os.path.join(__main__.work_directory, __main__.artifact_name)
    
    if __main__.artifact_name2:
        finalpath2 = __main__.os.path.join(path, __main__.artifact_name2)
    else:
        #Check if manifest.yml exist then try to upload
        finalpath2 = __main__.os.path.join(path, 'manifest.yml')
        if  __main__.os.path.exists(finalpath2):
            __main__.artifact_name2 = 'manifest.yml'
        else:
            finalpath2 = None
            
        
    
    if ('tar.gz' in __main__.artifact_name):
        pass
    
    longname, file_extension = __main__.os.path.splitext(__main__.artifact_name)
    
    #artname_lst = __main__.artifact_name.split("-", 10)
    artname_lst = longname.split("-", 10)
    
    #ver = re.search(r"\d*\.\d*\.\d*[.\d]*[-]*[0-9A-z]*", longname)
    ver = re.search(r"\d*\.\d*\.\d*[.\d]*[-]*[+]*[0-9A-Za-z]*[.]*[0-9a-zA-Z]*[+]*[0-9a-zA-Z]*", longname)
    
    if ver:
        if __main__.debug == 1:
            print("Version number found: ", ver.group(0))
    else:
        print("No version number found in file name specified")
        return __main__.sys.exit(1)
    
    actual_artifact_name = re.sub(r"\d*\.\d*\.\d*[.\d]*[-]*[+]*[0-9A-Za-z]*[.]*[0-9a-zA-Z]*[+]*[0-9a-zA-Z]*", '', longname)
    
    if actual_artifact_name.endswith("-"):
        actual_artifact_name = actual_artifact_name[:-1]
        
    if file_extension == '.war':
        versionnumber = ver.group(0)
        extension = 'war'
        # actual_artifact_name = '-'.join(artname_lst[:-1])
    elif file_extension == '.zip':
        # versionnumber = artname_lst[-1].strip(file_extension)
        versionnumber = ver.group(0)
        extension = 'zip'
        # actual_artifact_name = '-'.join(artname_lst[:-1])
    else:
        extension = file_extension[1:]
        versionnumber = ver.group(0)
        # actual_artifact_name = '-'.join(artname_lst[:-1])
    
    if __main__.debug == 1:
        print("Group ID: ", __main__.group_id)
        print("Artifact ID: ", actual_artifact_name)
        print("Version number: ", versionnumber)
        print("Extension: ", extension)
    
    files = {
        'maven2.groupId': (None, __main__.group_id),
        'maven2.artifactId': (None, actual_artifact_name),
        'maven2.version': (None, versionnumber),
        'maven2.asset1': ( __main__.artifact_name, open(finalpath, 'rb')),
        'maven2.asset1.extension': (None, extension),
        'maven2.generate-pom': (None, True) 
    }
    
    if __main__.artifact_name2:
        fn, fe = __main__.os.path.splitext(__main__.artifact_name2)
        try:
            files['maven2.asset2'] = ( __main__.artifact_name2, open(finalpath2, 'rb'))
        except FileNotFoundError:
            print("ERROR: File not found : ",__main__.artifact_name2)
            return __main__.sys.exit(2)
        files['maven2.asset2.classifier'] = (None, fn)
        files['maven2.asset2.extension'] = (None, fe[1:])

    response = __main__.requests.post(url=__main__.repository_full_url, params=params, files=files, auth=__main__.auth, proxies=__main__.proxies, verify=False)
    if __main__.debug == 1:
        print("Detailed response: ", response.content)
    if response.status_code == 204:
        print("Nexus Upload successful")
        return __main__.sys.exit(0)
    elif response.status_code == 400 and ("release" in __main__.repository_name or "staging" in __main__.repository_name):
        print("Nexus Upload failed. {}".format(response.json()[0].get('message')))
        return __main__.sys.exit(1)
    else:
        print("Nexus Upload failed. {}".format(response.json()[0].get('message')))
        print("Status code: ", response.status_code)
     
        return __main__.sys.exit(1)
