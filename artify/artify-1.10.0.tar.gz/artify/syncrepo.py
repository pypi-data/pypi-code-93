import __main__
import re
from artify import change_version

def commit_push_changes(message):
    print("INFO: Committing changes")
    
    version = None
    
    git_tag_command = ''
    git_push_command = ''
    
    path = __main__.os.path.abspath(__main__.os.getcwd())   
    
    ci_user = ''
    ci_user_email = ''
    
    if __main__.os.environ.get('GITLAB_USER_LOGIN'):
        ci_user = __main__.os.environ.get('GITLAB_USER_LOGIN')
    
    if __main__.os.environ.get('GITHUB_REPOSITORY_OWNER'):
        ci_user = __main__.os.environ.get('GITHUB_REPOSITORY_OWNER')
        
    if __main__.os.environ.get('GITHUB_OWNER'):
        ci_user = __main__.os.environ.get('GITHUB_OWNER')
        
    if __main__.os.environ.get('GITLAB_USER_EMAIL'):
        ci_user_email = __main__.os.environ.get('GITLAB_USER_EMAIL')
    
    if __main__.os.environ.get('GITHUB_USER_EMAIL'):
        ci_user_email = __main__.os.environ.get('GITHUB_USER_EMAIL')
    
    if message == 'tag':
        if __main__.os.path.exists(__main__.os.path.join(path,'build.gradle')):
            __main__.arch_type = 'gradle'
            filepath = __main__.os.path.join(path,'build.gradle')
            version = change_version.get_version(filepath, 'standard')
        
        if __main__.os.path.exists(__main__.os.path.join(path, 'app', 'build.gradle')):
            __main__.arch_type = 'gradle'
            filepath = __main__.os.path.join(path, 'app', 'build.gradle')
            version = change_version.get_version(filepath, 'standard')
        
        if __main__.os.path.exists(__main__.os.path.join(path,'package.json')):
            __main__.arch_type = 'npm'
            filepath = __main__.os.path.join(path, 'package.json')
            version = change_version.get_version(filepath, 'standard')

        if __main__.os.path.exists(__main__.os.path.join(path,'pom.xml')):
            __main__.arch_type = 'maven'
            filepath = __main__.os.path.join(path,'pom.xml')
            version = change_version.get_version(filepath, 'standard')

        if __main__.os.path.exists(__main__.os.path.join(path,'pubspec.yaml')):
            __main__.arch_type = 'flutter'
            filepath = __main__.os.path.join(path,'pubspec.yaml')
            version = change_version.get_version(filepath, 'standard')
            
        if __main__.os.path.exists(__main__.os.path.join(path, 'version.txt')):
            __main__.arch_type = 'other'
            filepath = __main__.os.path.join(path, 'version.txt')
            version = change_version.get_version(filepath, 'custom')

        if __main__.os.path.exists(__main__.os.path.join(path, 'setup.py')):
            __main__.arch_type = 'other'
            filepath = __main__.os.path.join(path, 'setup.py')
            version = change_version.get_version(filepath, 'custom')
            
        if __main__.os.path.exists(__main__.os.path.join(path, 'config/app.php')):
            __main__.arch_type = 'other'
            filepath = __main__.os.path.join(path, 'config/app.php')
            version = change_version.get_version(filepath, 'custom')
            
        if __main__.os.path.exists(__main__.os.path.join(path, 'config/app_config.php')):
            __main__.arch_type = 'other'
            filepath = __main__.os.path.join(path, 'config/app.php_config')
            version = change_version.get_version(filepath, 'custom')
            
        if __main__.debug == 1:
            print("DEBUG: Project type found: ", __main__.arch_type)

        # To-do Extract version number for .NET type project

        if version == None:
            print("INFO: No version number found. Defaulting to 1.0.0 for tagging.")
            version = '1.0.0'

        commit_sha = __main__.os.environ.get('CI_COMMIT_SHORT_SHA')
        git_tag_command = "git tag v{}-{}".format(version, commit_sha)
        process_git_tag = __main__.Popen(git_tag_command, shell=True, stdout=__main__.PIPE, cwd=path)
        print("INFO: Tag v{} created".format(version))
    else:   
        git_commit_command = "git config --global user.name {}; git config --global user.email {}; git commit -am '{}'".format(ci_user, ci_user_email, message)        
        process_git_commit = __main__.Popen(git_commit_command, shell=True, stdout=__main__.PIPE, cwd=path)
        print("INFO: Commit result: ", process_git_commit.communicate()[0])
    
    if __main__.os.environ.get('PRIVATE_TOKEN') == None:
        print("ERROR: Private token missing. Please add PRIVATE_TOKEN to Environment variables")
        __main__.os.sys.exit(1)
    

        
    auth = "//" + ci_user + ":" + __main__.os.environ.get('PRIVATE_TOKEN') + "@"

    repository_url = __main__.os.environ.get("CI_REPOSITORY_URL")
    # To-do: get repository url from git command
    #git config --get remote.origin.url
    

        
    ## Repository url with token
    ci_repo_url  = re.sub("//.*?@", auth, repository_url)
    
    if __main__.branch == '' and message != 'tag':
        __main__.branch = 'develop'
    
    if __main__.branch == '' and message == 'tag':
        __main__.branch = 'master'
      

    ##git_push_command = "git push origin {}".format(os.environ.get('CI_COMMIT_BRANCH'))
    
    # To-do Delete branch after merge with feature/patch-version, feature/minor-version, feature/major-version, feature/release-version
    # delete branch locally
    # git branch -d localBranchName

    # delete branch remotely
    # git push origin --delete remoteBranchName
    
    if message == 'tag':
        print("INFO: Pushing tags to repository:::")
        git_push_command = "git config user.name {}; git config user.email {}; git push --tags {} HEAD:{}".format(ci_user, ci_user_email, ci_repo_url, __main__.branch)
    else: 
        print("INFO: Pushing version changes:::")
        git_push_command = "git config --global user.name {}; git config --global user.email {}; git push {} HEAD:{}".format(ci_user, ci_user_email, ci_repo_url, __main__.branch)
 
    ##git_push_command = "git config user.name {}; git config user.email {}; git push {} HEAD:{}".format(os.environ.get('GITLAB_USER_LOGIN'), os.environ.get('GITLAB_USER_EMAIL'), ci_repo_url, os.environ.get('CI_COMMIT_BRANCH'))
    process_git_push = __main__.Popen(git_push_command, shell=True, stdout=__main__.PIPE, cwd=path)
    print("INFO: Push result: ", process_git_push.communicate()[0])
