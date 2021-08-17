import uuid
import __main__
# import urllib.parse
from posixpath import join as urljoin
import json

# To-do Generate project key for sonarQube using API
#  curl -u admin:admin -X POST 
# 'http://localhost:9000/sonar/api/projects/
# create?key=myKey&name=test-project-latest&project=test-project-latest'

# To-do Generate UID for key in parameter above
def generate_uuid():
    return str(uuid.uuid1())

def setup_variables():
    if __main__.username == '':
        __main__.username = __main__.os.environ.get('SONAR_USERNAME')
        if __main__.username == '' or __main__.username is None:
            if __main__.debug == 1:
                print("INFO: Using default SonarQube username")
            __main__.username = 'admin'
    
    if __main__.password == '':
        __main__.password = __main__.os.environ.get('SONAR_PASSWORD')
        if __main__.password == '' or __main__.password is None:
            if __main__.debug == 1:
                print("INFO: Using default SonarQube password")
            __main__.password = 'admin'
    
    if __main__.project_name == '':
        __main__.project_name = __main__.os.environ.get('CI_PROJECT_NAME')   
        if __main__.project_name == '' or __main__.project_name == None:
            print("ERROR: Please specify SonarQube Project name")
            return __main__.sys.exit(1)
    if __main__.project_key == '':
        __main__.project_key = __main__.os.environ.get('CI_PROJECT_PATH_SLUG')
        if __main__.project_key == '' or __main__.project_key == None:
            print("ERROR: Please specify SonarQube Project key")
            return __main__.sys.exit(1)

def create_sonarq_project(name, projectkey):
    token_value = ''
    #project_key = generate_uuid()
    
    __main__.auth = (__main__.username, __main__.password)  
    
    params = (('key', projectkey),('name', name),('project', name),)
    
    token_params = (('name', name),)
    
    # sonar_full_url = urllib.parse.urljoin(__main__.sonarhost, 'api/projects/create')
    # token_full_url = urllib.parse.urljoin(__main__.sonarhost , 'api/user_tokens/generate')
    sonar_full_url = urljoin(__main__.sonarhost, 'api/projects/create')
    token_full_url = urljoin(__main__.sonarhost , 'api/user_tokens/generate')
    if __main__.debug == 1:
        print("Sonar full url: ", sonar_full_url)
        print("Token full url: ", token_full_url)
    response = __main__.requests.post(url=sonar_full_url, params=params, proxies=__main__.proxies, auth=__main__.auth, verify=False)
    print("INFO: Creating SonarQube project: ",name)
    if __main__.debug == 1:
        print("Project creation response: ", response.content)
        print("Status code: ", response.status_code)
            
    if response.status_code == 200:
        print("INFO: SonarQube project created successfully.")
        print("INFO: Generating token for Project")
        token_response = __main__.requests.post(url=token_full_url, params=token_params, proxies=__main__.proxies, auth=__main__.auth, verify=False)
        
        if __main__.debug == 1:
            print("Token response: ", token_response.content)
        
        if token_response.status_code == 200:
            print("INFO: Project token generated successfully.")
            tkn_resp_obj = json.loads(token_response.content)   
            token_value = tkn_resp_obj.get('token')
            
        else:
            print("ERROR: ", token_response.content)
            return __main__.sys.exit(1)
           
        print("\nINFO: Sonar script below:")
        if __main__.language == 'java' and __main__.arch_type == 'maven':
            print("mvn sonar:sonar -Dsonar.projectKey={} -Dsonar.host.url={} -Dsonar.login={}".format(projectkey, __main__.sonarhost, token_value))
        
        if __main__.language.lower() == 'java' and __main__.arch_type.lower() == 'gradle':
            print("Declare org.sonarqube plugin in build.gradle file\n")
            print("plugins {\n   id \"org.sonarqube\" version \"3.0\"\n}\n")
            
            print("Windows command below:\n gradlew.bat sonarqube -Dsonar.projectKey={} -Dsonar.host.url={} -Dsonar.login={}".format(projectkey, __main__.sonarhost, token_value))
            print("\nLinux command below:\n gradle sonarqube -Dsonar.projectKey={} -Dsonar.host.url={} -Dsonar.login={}".format(projectkey, __main__.sonarhost, token_value))
            
        elif __main__.language.lower() in ['c#', 'vb.net']:
            print("\nSonarScanner.MSBuild.exe begin /k:\"{}\" /d:sonar.host.url=\"{}\" /d:sonar.login=\"{}\"".format(projectkey, __main__.sonarhost, token_value))
            print("\nMsBuild.exe /t:Rebuild")
            print("\nSonarScanner.MSBuild.exe end /d:sonar.login=\"{}\"".format(token_value))
        elif __main__.language.lower() in ['js', 'ts', 'go', 'python', 'php','other'] and __main__.arch_type.lower() in ['linux', 'macos']:
            print("sonar-scanner -Dsonar.projectKey={} -Dsonar.sources=. "\
              " -Dsonar.host.url={} "\
              " -Dsonar.login={} ".format(projectkey, __main__.sonarhost,token_value))
        
        elif __main__.language.lower() in ['js', 'ts', 'go', 'python', 'php','other'] and __main__.arch_type.lower() in ['windows', 'shell']:
            print("sonar-scanner.bat -D\"sonar.projectKey={}\" -D\"sonar.sources=.\""\
                  " -D\"sonar.host.url={}\" "\
                  " -D\"sonar.login={}\" ".format(projectkey, __main__.sonarhost, token_value))     
        else:
            print("sonar-scanner.bat -D\"sonar.projectKey={}\" -D\"sonar.sources=.\""\
                  " -D\"sonar.host.url={}\" "\
                  " -D\"sonar.login={}\" ".format(projectkey, __main__.sonarhost, token_value))        
        
        return __main__.sys.exit(0)
    elif response.status_code == 401:
        print("ERROR: Invalid username/password entered for SonarQube.")
        return __main__.sys.exit(1)
    elif response.status_code == 404:
        print("ERROR: Invalid SonarQube URL specified. URL not found.")
        return __main__.sys.exit(1)   
    else:
        message = ''
        
        try:
            resp_obj = json.loads(response.content)
            message = resp_obj.get('errors')[0].get('msg')
            print("ERROR: {}".format(message))
        except ValueError:
            message = 'Failed to create SonarQube project.'
            print("ERROR: {}".format(message))
        
        return __main__.sys.exit(1)
        
    