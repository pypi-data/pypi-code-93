import __main__

import os
import sys

##path = __main__.os.path.abspath(__main__.os.getcwd()) 
path = os.path.abspath(__main__.os.getcwd())

template_manifest = "project_name: <project_name>\ngroup_id: <group_id>\nartifact_id: <git_artifact_name>\nversion: 1.0.0"
template_gitlab_ci = "variables:\n   GIT_STRATEGY: clone\n\n" \
                   "stages:\n  - updates\n  - build\n  - test\n  - upload\n  - deploy\n  - security\n  - post-deploy\n\n" \
                    "search-commit:\n  stage: updates\n  script:\n     - echo Searching commit message for commands\n" \
                    "     - python -m artify -c extract\n  tags:\n    - <runner>\n\n" \
                    "build-project:\n  stage: build\n  script:\n   - echo Building project\n" \
                    "    #- <put buildscript here>\n  tags:\n    - <runner>\n\n" \
                    "build-project-production:\n  stage: build\n  script:\n     - echo Building project for production\n" \
                    "    #- <put production buildscript here>\n  only:\n    - master\n  tags:\n    - <runner>\n\n" \
                    "test-project:\n  stage: test\n  script:\n    - echo Peforming Test\n" \
                    "    #- <put test scripts here>\n  tags:\n    - <runner>\n\n" \
                    "sonar-scan:\n  stage: test\n  script:\n    - echo Peforming SonarQube scan\n" \
                    "    #- <sonar_qube_script>\n  tags:\n    - <runner>\n\n" \
                    "upload-project:\n  stage: upload\n  script:\n    - echo Uploading artifact to Nexus\n" \
                    "    #- python -m artify -c nexus -f <format> -n <artifact_name.zip/.war> -h <Nexus_repository_host>\n  tags:\n    - <runner>\n\n" \
                    "deploy-project:\n  stage: deploy\n  script:\n    - echo Deploying App to server\n" \
                    "    #- python -m artify -c deploy -f <manifest.yml> -h <awx_host>\n  tags:\n    - <runner>\n\n" \
                    "security-test-ibmappscan:\n  stage: security\n  script:\n    - echo Perform IBM AppScan Test\n" \
                    "    #- ibmscan.exe\n  tags:\n    - <security_runner>\n\n" \
                    "security-test-arachni:\n  stage: security\n  script:\n    - echo Perform Security Test\n" \
                    "    #- arachni <deploy_site_url>\n  tags:\n    - <security_runner>\n\n" \
                    "create-tag:\n  stage: post-deploy\n  script:\n    - echo Attempting to tag artifact\n" \
                    "    #- python -m artify -c syncrepo -m tag\n  only:\n    - master\n  tags:\n    - <runner>\n\n" \
    
def write_to_file(contents, filename):
    filepath = os.path.join(path, filename)
    if os.path.exists(filepath):
        print("File {} already exists".format(filename))
        return __main__.sys.exit(2)
    
    with open(filepath, 'w') as out_file:
        out_file.write(contents)
        
def generator(file):
    global template_manifest
    global template_gitlab_ci
    
    if file == 'manifest':
        write_to_file(template_manifest, 'manifest.yml')
        print("File manifest.yml generated successfully.")
        return __main__.sys.exit(0)
        
    elif file == 'gitlabci':
        write_to_file(template_gitlab_ci, '.gitlab-ci.yml')
        print("File .gitlab-ci.yml generated successfully.")
        return __main__.sys.exit(0)
    else:
        print("File not supported")
        return __main__.sys.exit(2)
        
        

    
    

    