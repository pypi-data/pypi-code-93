import re
import __main__
import json
from artify import change_version
from artify import syncrepo
    
#Extracts command from the commit message
def extract():
    print("INFO: Searching GIT commit message for commands")
    commit_message = __main__.os.environ.get('CI_COMMIT_MESSAGE')
    if not commit_message:
        print("INFO: Environment variable: CI_COMMIT_MESSAGE not set")
        git_commit_message_command = 'git show --summary'
        extracted_commit_message = __main__.Popen(git_commit_message_command, shell=True, stdout=__main__.PIPE, cwd=__main__.path)
        commit_message = str(extracted_commit_message.communicate()[0])
        print("INFO: Extracting last commit message with command: git show --summary")
        if not commit_message:
            __main__.sys.exit(0)
        if __main__.debug:
            print("DEBUG: Commit message extracted", commit_message)
            
    # commit_message = 'Test this message {"version": "patch", "archtype": "npm"}'
    
    try:
        found = re.search('{(.+?)}', commit_message)   
    
        if found:
            print("INFO: Processing commands")
            commands = convert_to_dict(found.group(1))
            if (commands.get('version') or commands.get('deltav')):
                
                if (commands.get('archtype') or commands.get('a')):
                    print("INFO: Executing version change")
                    if ((commands.get('archtype') == '' and commands.get('archtype') != None) or (commands.get('a') == '' and commands.get('a') != None)):
                        print("INFO: No version value specified. e.g major, minor, patch")
                        return __main__.sys.exit(0)
                    else:
                        if commands.get('archtype') == None:
                            __main__.arch_type = commands.get('a')
                        else:
                            __main__.arch_type = commands.get('archtype')
                        # Fetch version change
                        if commands.get('version') == None:
                            __main__.change_type = commands.get('deltav')
                        else:
                            __main__.change_type = commands.get('version')
                        
                        if commands.get('branch'):
                            __main__.branch = commands.get('branch')
                            print("INFO: Branch specified: ", __main__.branch)
                        if commands.get('file'):
                            __main__.version_file1 = commands.get('file')
                            
                        if commands.get('file2'):
                            __main__.version_file2 = commands.get('file2')
                            
                        # Fetch pre release value
                        if commands.get('preValue'):
                            __main__.pre_value = commands.get('preValue')
                        change_version.modify_version()
                        # Construct commit message
                        c_message =  'Change version: Type: ' + __main__.change_type
                        __main__.commit_message = c_message
                        syncrepo.commit_push_changes(__main__.commit_message)
                        return __main__.sys.exit(0)
                else:
                    print("INFO: No archtype specified")
                    return __main__.sys.exit(0)
            
        else:
            print("INFO: No commands to process")
            return __main__.sys.exit(0)
            
    except AttributeError:
        found = ''
        print("INFO: No commands specified")
        return __main__.sys.exit(0)

#Converts a string to a dictionary
def convert_to_dict(string):
    json_string = "{" + string + "}"
    if __main__.debug == 1:
        print('Command string: ', json_string)
    result = {}
    try:
        result = json.loads(json_string)
    except:
        print("ERROR: Format not supported")
        return result
    finally:
        return result

