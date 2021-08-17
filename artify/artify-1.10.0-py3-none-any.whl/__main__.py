import sys, getopt
import os
import requests
import base64
import json
from subprocess import Popen, PIPE

from artify import __version__, changelog

from artify import nexus
from artify import deploy
from artify import syncrepo
from artify import change_version
from artify import generate_file
from artify import extract_commands
from artify import initialize
from artify import archive
from artify import changelog

debug = 0;

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

proxies = {
  "http": None,
  "https": None,
}

# Variables - Nexus
nexus_format = ''
artifact_name = ''
artifact_name2 = ''
work_directory = ''
repository_name = ''
nexus_format = ''
repository_base_url = ''
repository_full_url = ''
username = ''
password = ''
directory = ''
group_id = ''
auth = ''

path = ''
# Variables - Nexus

# Variables - Deploy AWX
encoded_string = ''  
url = ''
debug = 0
# Variables - Deploy AWX

# Variables - Change version
arch_type = ''
pre_value = ''
version_file1 = ''
version_file2 = ''
nocommit = 0
fetch_version = 0
# Variables - Change version

# Variables - Sync repository
branch = ''
commit_message = ''
# Variables - sync repository

# Variables - create file
filename_gen = ''
# Variables - create file

# Variables - Initialize
sonarhost = ''
language = ''
project_key = ''
project_name = ''
# Variables - Initialize

# Variables - Archive
archive_basename = ''
archive_format = ''
archive_rootdir = ''
archive_basedir = ''
options = ''
# Variables - Archive

def main(argv):  
    print("Copyright \N{COPYRIGHT SIGN} 2020 - 2021 Stewartium ::: artify v{}\n".format(__version__))
    action = ''
    
    global path 
    path = os.path.abspath(os.getcwd()) 
    
    # Variables - Deploy AWX
    global encoded_string 
    global url
    global debug
    # Variables - Deploy AWX
    
    # Variables - Nexus
    global nexus_format 
    global artifact_name
    global artifact_name2
    global work_directory
    global repository_name
    global nexus_format
    global repository_base_url
    global repository_full_url
    global username
    global password
    global directory
    global group_id
    global auth
    # Variables - Nexus
    
    # Variables - Change version
    global arch_type
    global change_type
    global pre_value
    global version_file1
    global version_file2
    global nocommit
    global fetch_version
    # Variables - Change version
    
    global branch
    global commit_message
    
    
    # Variables - generate file
    global filename_gen
    
    # Variables - Initialize
    global sonarhost
    global language
    global project_key
    global project_name
    # Variables - Initialize
    
    # Variables - Global
    global archive_basedir
    global archive_format
    global archive_rootdir
    global archive_basename
    global options
    # Variables - Global
   
    try:
        opts, args = getopt.getopt(argv, "a:b:c:d:f:h:k:l:m:n:o:u:p:r:g:t:w:", ["command=", "help=", 
                                                "artifactname=", "repository=","groupid=", "directory=", "nexushost=",
                                                "file=", "awxhost=","--host=",
                                                "format=",
                                                "type=", "archtype=", "prevalue=","file2=","nocommit","getversion",
                                                "message=", "branch=",
                                                "projectkey=", "projectname=",
                                                "debug",
                                                "archivename=","rootdir=", "basedir=", "options="
                                               ])
    except getopt.GetoptError:
        print('Invalid syntax')
        print('To get help, type syntax below: ')
        print('python -m artify --help=')
        return sys.exit(2)
    
    for opt, arg in opts:
        if opt == "--help":
            if arg == "nexus":
                print("How to use Nexus Artifact Upload module\n")
                print("Usage: python -m artify -c nexus [OPTION] NEXUS_URL\n")
                print("Mandatory arguments: ")
                print("-f, --format    Nexus repository format e.g npm, maven, raw, nuget")
                print("-h, --nexushost   Nexus host base url e.g https://nexus.<yourcompany>.com")
                print("")
                print("Optional arguments i.e Some can be passed in the environment variables")
                print("-w, --workdirectory Working directory of artifact to be uploaded to Nexus repository")
                print("-n, --artifactname  Artifact name")
                print("-r, --repository    Nexus repository to upload to: e.g <repository>-snapshots")
                print("-g, --groupid       Group ID for Maven2 type repository")
                print("-d, --directory     Directory for RAW type repository")
                print("-u, --username      Username of nexus user")
                print("-p, --password      Password of nexus user")
                print("\n--proxy             Sets Http proxy")
                print("--proxysec          Sets Https proxy")
                return sys.exit(0)
            elif arg == "deploy":
                print("How to deploy app to AWX infrastructure")
                print('python -m artify -c deploy -f <manifest> -h <awx_host>')
                print("Or")
                print("python -m artify --command deploy --file <manifest> --awxhost <awx_host>")
                print("\n--proxy             Sets Http proxy")
                print("--proxysec          Sets Https proxy")
                return sys.exit(0)
            elif arg == "syncrepo":
                print('')
                print("How to Push and Commit changes\n")
                print("Usage: python -m artify -c syncrepo [OPTION] COMMIT_MESSAGE\n")
                print("Mandatory arguments: ")
                print("-m, --message     Commit message")
                print("\nOptional arguments: ")
                #print("-h, --host        Repository url")
                print("-b, --branch     Repository branch to sync changes")
                print("\n--proxy             Sets Http proxy")
                print("--proxysec          Sets Https proxy")
                return sys.exit(0)
            elif arg == "deltav" or arg == "version":
                print('')
                print('python -m artify -c deltav -t <version_change> -a <architecture_type>')
                print('python -m artify -c version -t <version_change> -a <architecture_type>')
                print("Or")
                print("python -m artify --command deltav --type <version_change> --archtype <architecture_type>")
                print("python -m artify --command version --type <version_change> --archtype <architecture_type>")
                print("Mandatory argument(s): ")
                print("-t, --type          Type of version change: major, minor, patch, auto")
                print("e.g --type major    1.0.0-alpha => 2.0.0-alpha")
                print("e.g --type minor    1.0.0       => 1.1.0")
                print("e.g --type patch    1.0.0-beta => 1.0.1-beta")
                print("e.g --type build    1.0.0.0 => 1.0.0.1   Experimental")
                print("e.g --type auto     1.0.0 => 1.0.0-build.1") 
                print("e.g --archtype npm, gradle, maven, flutter, dotnet, netcore")
                print("\nOptional arguments: ")
                print("-b, --branch        Branch to commit code changes. Default: develop")
                print("--preValue          Prerelease version value e.g SNAPHOT, RELEASE, BUILD, beta, alpa")
                print("--nocommit     Does not create feature branch with version change")
                print("--getversion   Fetches the current application version")
                print("-f, --file     File name that you want to update version number. It should be relative to artify execution directory ")
                print("--file2        An additional file that you want to update version number. It should be relative to artify execution")
                return sys.exit(0)
            elif arg == 'create':
                print('')
                print('python -m artify -c create -f <template_file>')
                print("Mandatory argument(s): ")
                print('-f, --file    Template file to create e.g manifest, gitlabci')
                return sys.exit(0)
            elif arg == 'extract':
                print('')
                print('python -m artify -c extract \n')
                print('Sample commit messages below: \n')
                print("Added login functionality {\"version\": \"patch\", \"archtype\": \"npm\", \"branch\": \"release\" } \n")
                print("Added edit functionality {\"version\": \"minor\", \"a\": \"flutter\" } \n")
                return sys.exit(0)
            elif arg == 'initialize':
                print('')
                print('python -m artify -c initialize -h <SonarQube_base_url> -u <username> -p <password> -a <arch_type/os> -l <language>')    
                print('\nExample command below for a java project that uses gradle build tool.')
                print('\npython -m artify -c initialize -h <SonarQube_base_url> -u <username> -p <password> -l java -a gradle\n')
                return sys.exit(0)
            elif arg == 'archive':
                print('Uses Shutil Python library to create archive file')
                print('python -m artify -c archive -n <archive_name> -f <archive_format> -w <root_dir> -d <base_dir>')
                print("Mandatory argument(s):")
                print("-n, --archivename  Name for the archive file that will be created")
                print("-f, --format       Format for the archive e.g dddddddd")
                print("-w, --rootdir      Root directory is a directory that will be the root directory of the archive.")
                print("-d, --basedir      Base directory is the directory where we start archiving from.")
                return sys.exit(0)
            elif arg == "changelog":
                print("python -m artify -c changelog --added add login functionality --changed=update from oauth2 to keycloak")
            else:
                print('python -m artify --help nexus        Help on how to deploy to Nexus Repository')
                print('python -m artify --help deploy       Help on how to deploy to AWX host')
                print('python -m artify --help syncrepo     Help on how to commit and push code to repository')
                print('python -m artify --help deltav       Help on how to change version number')
                print('python -m artify --help version       Help on how to change version number')
                print("python -m artify --help create       Help on how to generate template files")
                print("python -m artify --help extract      Help on how to use the extract command") 
                print("python -m artify --help archive      Help on how to use archive command")
                return sys.exit(0)
        elif opt == "--debug":
            debug = 1
        elif opt == "--nocommit":
            nocommit = 1
        elif opt == "--getversion":
            fetch_version = 1
        elif opt in ("-c", "--command"):
            action = arg
            if action == '':
                print("Invalid command specified")
                return sys.exit(2)
        elif opt == "--proxy":
            proxies['http'] = arg
        
        elif opt == "--proxysec":
            proxies['https'] = arg    
            
        elif opt == '--file2':
            if action == 'deltav' or action == 'version':
                version_file2 = arg 
            if action == 'nexus':
                artifact_name2 = arg
                if artifact_name2 == '':
                    print("Please specify second artifact name")
                    return sys.exit(2)
            # else:
            #     print("Invalid command specified: param: --file2")   
        ## Deploy-artifact-awx-host params START
        elif opt in ("-f", "--file", "--format"):
            if action == 'nexus':
                nexus_format = arg
                if nexus_format == '':
                    print("Please specify nexus repository format e.g npm, maven, raw, nuget")
                    return sys.exit(2) 
            elif action == 'deploy':
                file_path = os.path.join(path, arg)
                if os.path.exists(file_path):
                    with open(arg, "rb") as manifest_file:
                        encoded_string = base64.b64encode(manifest_file.read())
                else:
                    print("ERROR: File {} does not exist".format(arg))
                    return sys.exit(2)
            elif action == 'create':
                # Generate file START
                filename_gen = arg
                # Generate file END
            elif action == 'archive':
                archive_format = arg
                if archive_format == '':
                    print('Please specify archive format e.g zip, tar, gztar, bztar, xztar')
                    return sys.exit(2)
            elif action == 'deltav' or action == 'version':
                version_file1 = arg
            else:
                print("Invalid command specified: param: -f")
                     
        ## Deploy-artifact-awx-host params END
        
        ## Change-version-number params START
        elif opt in ("-t", "--type"):
            change_type = arg
             
        elif opt in ("-a", "--archtype"):
            arch_type = arg 
            
        elif opt == "--prevalue":
            pre_value = arg     
            
         ## Change-version-number params END
        
        ## Deploy-artifact-nexus params START
        ## -h 
        elif opt in ("-h", "--nexushost", "--awxhost", "--host"):
            if action == 'nexus':
                repository_base_url = arg
                if repository_base_url == '':
                    print("Nexus base url cannot be left blank")
                    return sys.exit(2)
            elif action == 'deploy':
                url = arg
            elif action == 'initialize':
                sonarhost = arg
            else:
                print("Invalid {} host specified".format(action))
                return sys.exit(2)
        ## -u
        elif opt in ("-u", "--username"):
            username = arg
            if username == '':
                print("Nexus username cannot be left blank")
        
        
        ## -p
        elif opt in ("-p", "--password"):
            password = arg
            if password == '':
                print("Nexus password cannot be left blank")
                return sys.exit(2)
        
        ## -d 
        elif opt in ("-d", "--directory", "--basedir"):
            if action == 'archive':
                archive_basedir = arg
            else:
                directory = arg
            if directory == '' and action == 'nexus':
                print("Please specify directory to store artifact for RAW respository")
                return sys.exit(2)
            
            if archive_basedir == '' and action == 'archive':
                print('Please specify base directory i.e the folder to be archived.')
                return sys.exit(2)
        
        ## -w
        elif opt in ("-w", "--workdirectory", "--rootdir"):
            if action == 'archive':
                archive_rootdir = arg
            else:
                work_directory = arg
            if work_directory == '' and action == 'nexus':
                work_directory = path
                if work_directory == '':
                    print("Please specify artifact current directory")
                    return sys.exit(2)
            if archive_rootdir == '' and action == 'archive':
                archive_rootdir = path
                if archive_rootdir == '':
                    print('Please specify root directory for artifact.')
                    return sys.exit(2)
         
        ## -n  
        elif opt in ("-n", "--artifactname", "--projectname", "--archivename"):
            if action == 'initialize':
                project_name = arg
            elif action == 'archive':
                archive_basename = arg
                if archive_basename == '':
                    print('Please specify archive name e.g myfile')
                    return sys.exit(2)
            else:
                artifact_name = arg
                if artifact_name == '':
                    print("Please specify artifact name")
                    return sys.exit(2)
        
        ## -g
        elif opt in ("-g", "--groupid"):
            group_id = arg
            if group_id == '':
                print("Please specify Group ID")
                return sys.exit(2)
                  
                  
        ## -r
        elif opt in ("-r", "--repository"):
            repository_name = arg
            if repository_name == '':
                print('Please specify repository name')
                return sys.exit(2)
        ## Deploy-artifact-nexus params START
        
        ## Change version (deltav) START
        elif opt in ("-t", "--type"):
            change_type = arg
            
        ## Change version (deltav) END
        elif opt in ("-m", "--message"):
            commit_message = arg
        elif opt in ("-b", "--branch"):
            branch = arg
        ## Commit-push changes repository START
        
        
        ## Commit-push changes repository END
        
        # Make archive START
        elif opt in ("-o", "--options"):
            options = arg
            
        # Make archive END
        
        # Initialize START
        elif opt in ("-l", "--language"):
            language = arg
            
        elif opt in ("-k", "--projectkey"):
            project_key = arg
        # Initialize END       
         
    if debug == 1:
        print("DEBUG: Action entered: ", action)
    if action == 'nexus':
        nexus.setup_variables()
        print("INFO: Nexus Format entered: ", nexus_format)
        if nexus_format == 'raw':
            nexus.upload_nexus_raw()
        elif nexus_format == 'npm':
            nexus.upload_nexus_npm()
        elif nexus_format == 'maven':
            nexus.upload_nexus_maven()
        else:
            print("Invalid nexus format entered")
            return sys.exit(2)
            
    elif action == 'deltav' or action == 'version':
        change_version.modify_version()
    elif action == 'syncrepo':
        syncrepo.commit_push_changes(commit_message)
    elif action == 'deploy':
        deploy.deploy_app_awx()
    elif action == 'create':
        generate_file.generator(filename_gen)
    elif action == 'document':
        #document artifact changes
        pass
    elif action == 'changelog':
        changelog.update_changelog()
    elif action == 'extract':
        extract_commands.extract()   
    elif action == 'initialize':
        #initialize.create_sonarq_project('test-frontend', 'goj-migration')   
        initialize.setup_variables()
        initialize.create_sonarq_project(project_name, project_key)
    elif action == 'archive':           
        result = archive.archive_file()
        if result == '' or result == None:
            print("Error: Failed to archive file.")
        else:
            print("INFO: File {} archived successfully.".format(result))
    elif action == '':
        print("Invalid action specified")
        return sys.exit(2)
    else:
        print("Action not supported")
        return sys.exit(2)
    
    return sys.exit(0) 
    
if __name__ == "__main__":
    main(sys.argv[1:])    
        
        