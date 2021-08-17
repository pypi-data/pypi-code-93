import __main__
import fileinput
import re
from glob import glob
from artify import utilities

path = __main__.os.path.abspath(__main__.os.getcwd()) 

def get_version_unix(project_type):
    retrieve_ver_command = ''
    retrieve_ver_command2 = ''
    ## check type of project
    if project_type == 'npm':
        retrieve_ver_command  = "grep 'version\s*:\s*' package.json"
    if project_type == 'java':
        retrieve_ver_command = "grep 'version"
    if project_type == 'android':
        retrieve_ver_command1 = "grep 'versionCode\s*' app/build.gradle"
        retrieve_ver_command2 = "grep 'versionName\s*' app/build.gradle"
    if project_type == 'flutter':
        retrieve_ver_command = "grep 'version\s*:\s*' pubspec.yaml"
    if project_type == 'dotnet':
        retrieve_ver_command = ''
    if project_type == 'netcore':
        retrieve_ver_command = ''  
            
def get_version(filename, vtype):
    result = 1
    version_string = ''
    version_code = ''  
    versionstr = ''
    
    global path
    
    if __main__.os.path.exists(filename):
        with open(filename) as origin_file:
            for line in origin_file:
                if __main__.arch_type == 'npm' and re.search(r'version"\s*:', line):
                    result = 0
                    versionstr = line
                    break
                if __main__.arch_type == 'gradle' and re.search(r'version =', line):
                    result = 0
                    versionstr = line
                    break     
                if __main__.arch_type == 'gradle' and re.search(r'versionName', line):
                    result = 0
                    versionstr = line
                if __main__.arch_type == 'gradle' and re.search(r'versionCode', line):
                    result = 0
                    version_code = line 
                if __main__.arch_type == 'maven' and re.search(r'<version>', line):
                    result = 0
                    versionstr = line
                    break                
                if __main__.arch_type == 'flutter' and re.search(r'version:', line):
                    result = 0
                    versionstr = line
                    break                
                if __main__.arch_type == 'dotnet' and re.search(r'assembly: AssemblyFileVersion', line):
                    result = 0
                    versionstr = line
                    break                    
                if __main__.arch_type == 'netcore' and re.search(r'<AssemblyVersion>', line):
                    result = 0
                    versionstr = line
                    break  
                if vtype == 'custom' and re.search(r"\d*\.\d*\.\d*[.\d]*[-]*[+]*[0-9A-Za-z]*[.]*[0-9a-zA-Z]*[+]*[0-9a-zA-Z]*", line):
                    result = 0
                    versionstr = line
                    break                 

    else:
        print("INFO: Could not find file with version number")
        return __main__.sys.exit(2)
    
    if __main__.debug == 1:
        print("DEBUG: File searched for version number: ", filename)
        print("DEBUG: Version string: ", versionstr)

    if __main__.arch_type == 'npm' and vtype == 'standard':
        print("INFO: Architecture::: Typescript/Javascript: NPM build")
        strip_version = versionstr.strip()
        split_version = strip_version.split(":")
        version_string = re.sub('[,"]', '', split_version[1])   
        version_string = version_string.strip() 
            
    elif __main__.arch_type == 'gradle' and vtype == 'standard':
        java_android_build_file = __main__.os.path.join(path, 'app','build.gradle')
        if __main__.os.path.exists(java_android_build_file):
            print("INFO: Architecture::: Java Android: Gradle build")
            strip_version = versionstr.strip()
            split_version = strip_version.split(" ")
            version_string = re.sub('["]', '', split_version[1].strip())
            
            strip_versionCode = version_code.strip()
            split_version_code = strip_versionCode.split(" ")
            version_string = version_string + "+" + split_version_code[1].strip()
            
        else:
            print("INFO: Architecture::: Java : Gradle build")
            strip_version = versionstr.strip()
            split_version = strip_version.split("=")
            version_string = re.sub("[']", '', split_version[1].strip())
            if (__main__.debug == 1):
                print("DEBUG: Version String: Gradle: ", version_string)
        
        
    elif __main__.arch_type == 'flutter' and vtype == 'standard':
        print("INFO: Architecture::: Flutter")
        strip_version = versionstr.strip()
        split_version = strip_version.split(" ")
        version_string = re.sub("[']", '', split_version[1].strip())
    
    elif __main__.arch_type == 'maven' and vtype == 'standard':
        print("INFO: Architecture::: Java : Maven build")
        strip_version = versionstr.strip()
        version_string = re.sub('<[^<]+>', '', strip_version)
        version_string = version_string.strip()
             
    elif __main__.arch_type == 'dotnet' and vtype == 'standard':
        print("INFO: Architecture::: .NET/C# : MSbuild")
        strip_version = versionstr.strip()
        clean_ver1 = re.sub('assembly: AssemblyFileVersion', '', strip_version)
        clean_ver2 = re.sub('[\[(")\]]*', '', clean_ver1)
        version_string = re.sub("[']", '', clean_ver2.strip())
        
    elif __main__.arch_type == 'netcore' and vtype == 'standard':
        print("INFO: Architecture::: .NetCore/C# ")
        strip_version = versionstr.strip()
        version_string = re.sub('<[(^<]+>', '', strip_version)
        version_string = version_string.strip()
        

    if vtype == 'custom':
        strip_version = versionstr.strip()
        version_string_tmp = re.search(r"\d*\.\d*\.\d*[.\d]*[-]*[+]*[0-9A-Za-z]*[.]*[0-9a-zA-Z]*[+]*[0-9a-zA-Z]*", strip_version)
        if (__main__.debug == 1):
            print("DEBUG: Version String: Custom: ", version_string_tmp)
        if version_string_tmp:
            version_string = version_string_tmp.group(0)
       
        else:
            print("ERROR: No version detected in file:::",filename)
            return __main__.sys.exit(2)
    
    return version_string    

def process_version(versionstr):
    major = 0
    minor = 0
    patch = 0 
    build = 0
    
    new_prebuild = 0
    
    global path
    
    versionCode = 0
    
    current_version = ''
    prelease_version = ''
    version_lst = []
    new_version = ''
    
    if __main__.debug == 1:
        print("DEBUG: Version string:: Process Version:: ", versionstr)
    
    if __main__.arch_type == 'flutter':
        version_str, versionCode = versionstr.split("+") 
        versionCode = int(versionCode) + 1
    elif __main__.arch_type == 'gradle':
        java_android_build_file = __main__.os.path.join(path, 'app', 'build.gradle')
        if __main__.os.path.exists(java_android_build_file):
            version_str, versionCode = versionstr.split("+")
            versionCode = int(versionCode) + 1
        else:
            version_str = versionstr
    else: 
        version_str = versionstr

    
    if version_str == '':
        print("INFO: No version number detected:: Blank")
        return __main__.sys.exit(2)    
    # Semantic version standard A pre-release version MAY be denoted by appending a hyphen and a series of dot separated identifiers 
    # immediately following the patch version.
    check_prerelease = version_str.split("-") 
    if len(check_prerelease) == 1:
        current_version = check_prerelease[0]
    else:
        current_version = check_prerelease[0]
        check_prerelease.pop(0) # remove main version number
        prelease_version = '-'.join(check_prerelease)        
              
    version_lst = current_version.split(".")
    
    if (len(version_lst) == 4):
        version_format = "modified"
        major, minor, patch, build = version_lst
    else:
        version_format = "standard"
        major, minor, patch = version_lst
        
    if __main__.debug == 1:
        print("DEBUG: Before update::: Major: {} :: Minor: {} :: Patch :: {}".format(major, minor, patch))
        print("DEBUG: Version format: ", version_format)
        print("DEBUG: Prerelease value: ", prelease_version)
        
    
    if not (major.isdigit() and minor.isdigit() and patch.isdigit()):
        
        #print("No version number detected::: ")
        ## This is the main version number, have to get it from file1 or file2
        #if (__main__.version_file1 or __main__.version_file2):
        #    pass
        print('ERROR: Invalid version number found')
        return __main__.sys.exit(2)
    
    if not hasattr(__main__, 'change_type'):
    #if not hasattr(__main__, 'change_type') and not hasattr(__main__, 'fetch_version'):
        print("ERROR: No change type specified e.g patch, minor, major")
        return __main__.sys.exit(2)

    
    if __main__.change_type == "major":
        major = int(major) + 1
        if version_format == "standard":
            minor = 0
            patch = 0
        else:
            minor = 0
            patch = 0
            build = 0         
        
    if __main__.change_type == "minor":    
        minor = int(minor) + 1  
        patch = 0
        if version_format != "standard":
            build = 0

    if __main__.change_type == "patch":
        patch = int(patch) + 1
        if version_format != "standard":
            build = 0

    if __main__.change_type == "build":
        build = int(build) + 1    
        
    if __main__.change_type == "auto":

        if prelease_version != '':
            current_pre_build = re.sub("\D", "", prelease_version)
            if current_pre_build != '':
                new_prebuild = int(current_pre_build) + 1
                current_pre_string = re.sub("\s*", "", prelease_version)
                if current_pre_string != '':
                    prelease_version = prelease_version.replace(str(current_pre_build), str(new_prebuild))
                else:
                    prelease_version = 'build.' + new_prebuild
            else:
                prelease_version = 'build.1'
        else:
            prelease_version = 'build.1'
            
        if __main__.debug == 1:
            print("DEBUG: Updated: Prerelease value: ", prelease_version)
    
    if __main__.change_type == "prerelease":
        if __main__.debug == 1:
            print("DEBUG: Prerelease version value: ", __main__.pre_value)
        prelease_version = __main__.pre_value

    if __main__.debug == 1:
        print("DEBUG: After update::: Major: {} :: Minor: {} :: Patch :: {}".format(major, minor, patch))
    
    if version_format == "standard":
        new_version = str(major) + '.' + str(minor) + '.' + str(patch)
    else:
        new_version = str(major) + '.' + str(minor) + '.' + str(patch) + '.' + str(build)
        
    if prelease_version != '' and (__main__.change_type == 'prerelease' or __main__.change_type == 'auto'):
        if prelease_version.startswith("+"):
            new_version = new_version + prelease_version
        elif prelease_version.startswith("-"):
            new_version = new_version + prelease_version
        else:
            new_version = new_version + '-' + prelease_version
    
    if __main__.arch_type == 'flutter':
        new_version = new_version + "+" + str(versionCode)
    elif __main__.arch_type == 'gradle':
        java_android_build_file = __main__.os.path.join(path, 'app', 'build.gradle')
        if __main__.os.path.exists(java_android_build_file):
            new_version = new_version + "+" + str(versionCode)
             
               
    return new_version      
        
         
            
        
def replace_version(filename, search_text, replacement_text):
    try:
        with fileinput.FileInput(filename, inplace=True, backup='') as file:
            for line in file:
                print(line.replace(search_text, replacement_text), end='')
    except FileNotFoundError:
        print("ERROR: File {} not found. ".format(filename))
        return __main__.sys.exit(2)
                
          
            
def change_version_file(filepath, version, newversion):
    global path
    if __main__.debug == 1:
        print("DEBUG: Old version: ", version)
        print("DEBUG: New version: ", newversion)
        print("DEBUG: File path: ", filepath)
    old_version = ''
    new_version = ''
    
    if __main__.arch_type == 'npm':
        old_version = "\"version\": \"{}\",".format(version)
        new_version = "\"version\": \"{}\",".format(newversion)
        replace_version(filepath, old_version, new_version)
        
    if __main__.arch_type == 'flutter':
        old_version = "version: {}".format(version)
        new_version = "version: {}".format(newversion)
        replace_version(filepath, old_version, new_version)  
    
    if __main__.arch_type == 'maven': 
        old_version = "<version>{}</version>".format(version)
        new_version = "<version>{}</version>".format(newversion)
        replace_version(filepath, old_version, new_version)
    if __main__.version_file1:
        old_version = "{}".format(version)
        new_version = "{}".format(newversion)
        replace_version(filepath, old_version, new_version)          
    if __main__.version_file2:
        old_version = "{}".format(version)
        new_version = "{}".format(newversion)
        replace_version(filepath, old_version, new_version)   
     
    if __main__.arch_type == 'gradle':
        java_android_build_file = __main__.os.path.join(path, 'app/build.gradle')
        if __main__.os.path.exists(java_android_build_file):
            ovn, ovc = version.split("+")
            nvn, nvc = newversion.split("+")
            old_version_name = "versionName \"{}\"".format(ovn)
            new_version_name = "versionName \"{}\"".format(nvn)
            old_version_code = "versionCode {}".format(ovc)
            new_version_code = "versionCode {}".format(nvc)
            replace_version(filepath, old_version_name, new_version_name)
            replace_version(filepath, old_version_code, new_version_code)
        else:
            old_version = "version = '{}'".format(version)
            new_version = "version = '{}'".format(newversion)
            replace_version(filepath, old_version, new_version)        
            
    if __main__.arch_type == 'dotnet':
        old_version = "AssemblyFileVersion(\"{}\")".format(version)
        new_version = "AssemblyFileVersion(\"{}\")".format(newversion)
        replace_version(filepath, old_version, new_version)        
    
    if __main__.arch_type == 'netcore':
        old_version = "<AssemblyVersion>{}</AssemblyVersion>".format(version)
        new_version = "<AssemblyVersion>{}</AssemblyVersion>".format(newversion)
        replace_version(filepath, old_version, new_version)      
         
def change_manifest(v, dv):
    ## Retreive version number manifest
    ## grep "version\s*=\s*" manifest.yml  ## To-do Refactor to use this 
    
    global path
    file_path = __main__.os.path.join(path, 'manifest.yml')
    if __main__.os.path.exists(file_path):
        old_version = "version: {}".format(v)
        new_version = "version: {}".format(dv)
        replace_version(file_path, old_version, new_version)
        print("INFO: manifest.yml updated successfully.")
    else:
        if __main__.debug == 1:
            print("INFO: No manifest.yml file exist")
    
    
    ## check if manifest.yml exist
    ## sed_command_manifest = "sed -i 's/version: {}/version: {}/g' ./manifest.yml".format(v.rstrip(), dv)
 
    ## update version number in manifest.yml
    ##process_sed_manifest = __main__.Popen(sed_command_manifest, shell=True, stdout=__main__.PIPE, cwd=path)

def modify_version():

        
    new_version = ''
    curr_version = ''
    version_format = ''
    version_file = ''

    global path   
    if __main__.debug == 1:
        print("DEBUG: Working directory: ",path)
    
    search_ver_text = ''
    
    if __main__.fetch_version == 1:
        fetched_version = utilities.get_current_application_version(path)
        if fetched_version:
            print("RESULT: Current App version: ", fetched_version)
        else:
            print("INFO: Could not find current application version")
        return __main__.sys.exit(0)
    
    git_checkout_command = "git checkout -b feature/modify-version"
    if not (__main__.nocommit):
        process_checkout_command = __main__.Popen(git_checkout_command, shell=True, stdout=__main__.PIPE, cwd=path)
        print("Checkout result: ", process_checkout_command.communicate()[0])
    
    if __main__.arch_type == 'npm':
        version_file = 'package.json'
        search_ver_text = "\"version\": v" 
        
    if __main__.arch_type == 'flutter':
        version_file = 'pubspec.yaml'
        ## updaet version code and name
        
    if __main__.arch_type == 'gradle':
        java_android_build_file = __main__.os.path.join(path, 'app','build.gradle')
        if __main__.os.path.exists(java_android_build_file):
            version_file = 'app/build.gradle'
            ## update versionCode and versionName
        else:
            version_file = 'build.gradle'
    if __main__.arch_type == 'maven':
        version_file = 'pom.xml'      
    if __main__.arch_type == 'dotnet':
        file_list = glob('*.sln') 
        if len(file_list) >= 1:
            filename, filextension = __main__.os.path.splitext(file_list[0])
            version_file = __main__.os.path.join(filename, 'Properties', 'AssemblyInfo.cs') 
        else:
            print("ERROR: Could not file solution file (*.sln)")
            return __main__.sys.exit(2)
    if __main__.arch_type == 'other':
        version_file = __main__.version_file1
    
    if __main__.arch_type == 'netcore':
        version_file = __main__.version_file1
   
    
    filepath = __main__.os.path.join(path, version_file)

    
    filepath_1 = __main__.os.path.join(path, __main__.version_file1)
    filepath_2 = __main__.os.path.join(path, __main__.version_file2)
    curr_version = get_version(filepath, 'standard')
    ## check if version is a real version number
    ver_found = re.search(r"\d*\.\d*\.\d*[.\d]*[-]*[+]*[0-9A-Za-z]*[.]*[0-9a-zA-Z]*[+]*[0-9a-zA-Z]*", curr_version)
    if (ver_found != None):
        curr_version = ver_found.group(0)
    else:
        if (__main__.debug == 1):
            print("INFO: No version number found in file:::",version_file)
        if (__main__.version_file1):
            curr_version = get_version(filepath_1, 'custom')
            ver_found = re.search(r"\d*\.\d*\.\d*[.\d]*[-]*[+]*[0-9A-Za-z]*[.]*[0-9a-zA-Z]*[+]*[0-9a-zA-Z]*", curr_version)
            
            if not (ver_found):
                print("Error: No version detected::: --file")
                return __main__.sys.exit(2)
                        

    if __main__.debug == 1:
        print("DEBUG: Current version: ", curr_version)
    new_version = process_version(curr_version)

    change_manifest(curr_version, new_version)  ## Update manifest file
    if (__main__.version_file1):
        change_version_file(__main__.version_file1, curr_version, new_version)
    if (__main__.version_file2):
        change_version_file(__main__.version_file2, curr_version, new_version)
    change_version_file(filepath, curr_version, new_version)

    print("INFO: Previous version: ", curr_version, "  New Version:: ", new_version, "   Type: ", __main__.change_type)
    
  