import __main__


def deploy_app_awx():
    headers = {'Content-Type': 'application/json', 'X-Baaskit-Deploy-Token': __main__.os.environ.get('DEPLOY_TOKEN')}
    
    manifest_data = __main__.encoded_string.decode(encoding="utf-8")
    manifest_dat = manifest_data.rstrip()
            
    data = {"commit_ref_name": __main__.os.environ.get('CI_COMMIT_REF_NAME'),
        "job_id": __main__.os.environ.get('CI_JOB_ID'),
        "job_name": __main__.os.environ.get('CI_JOB_NAME'),
        "manifest": manifest_dat,
        "project_name": __main__.os.environ.get('CI_PROJECT_NAME'),
        "short_sha": __main__.os.environ.get('CI_COMMIT_SHORT_SHA'),
        "user_email": __main__.os.environ.get('GITLAB_USER_EMAIL'),
        "username": __main__.os.environ.get('GITLAB_USER_NAME')    
    }
    
    
    reqdata = __main__.json.dumps(data)
    
    if __main__.debug == 1:
        print("Manifest B64: ", __main__.encoded_string.decode(encoding="utf-8"))
        print('Ref: ', __main__.os.environ.get('CI_COMMIT_REF_NAME'))
        print('Email: ', __main__.os.environ.get('GITLAB_USER_EMAIL'))
        print('Username: ', __main__.os.environ.get('GITLAB_USER_NAME'))
        print('Token: ', __main__.os.environ.get('DEPLOY_TOKEN'))
        print('Job ID: ', __main__.os.environ.get('CI_JOB_ID'))
        print('Project name: ', __main__.os.environ.get('CI_PROJECT_NAME'))
        print('User email: ', __main__.os.environ.get('GITLAB_USER_EMAIL'))
        print("Short SHA: ", __main__.os.environ.get('CI_COMMIT_SHORT_SHA'))
        print('Username: ', __main__.os.environ.get('GITLAB_USER_NAME'))
            
    response = __main__.requests.post(url=__main__.url, data=reqdata, proxies=__main__.proxies, headers=headers, verify=False)

    print("HTTP Response code: ",response.status_code)
    print("HTTP Response body: ",response.content.strip())
    
    if response.status_code == 200:
        print("INFO: Completed successfully.")
        return __main__.sys.exit(0)    
    else:
        print("ERROR: Deployment failed.")
        return __main__.sys.exit(1)
