from github import Github
import base64
import requests
from requests.api import head
from yaml import dump

"""
" The client will interact with a GitHub Repository using the GitHub API and package PyGithub
" docu: https://docs.github.com/en/rest
" docu: https://pygithub.readthedocs.io/en/latest/introduction.html
"
"""

class GitHubClient():
    
    def __init__(self, username, token, repo_name, branch, enterprise_name=None):
        """
        @param::username: GitHub account username
        @param::token: authentication token to access account
        @param::repo_name: name of current working repository 
        @param::enterprise_name: hostname for specific GitHub enterprise website
        @param::versioning: Boolean whether user wants to version or not
        return GitHub Client Instance
        """ 
        if username == None:
            raise Exception('GitHub username is required.')
        elif token == None:
            raise Exception('GitHub token is required.')
        elif repo_name == None:
            raise Exception('GitHub repository name is required.')
        elif branch == None:
            raise Exception('GitHub branch is required.')

        if enterprise_name == None:
            github = Github(username, token)
            self.repository = github.get_user().get_repo(repo_name)
        else:
            github = Github(base_url="https://" + enterprise_name + "/api/v3", login_or_token=token)
            self.repository = github.get_user().get_repo(repo_name)
        
        self.username = username
        self.token = token
        self.repo_name = repo_name
        self.branch = branch
        self.enterprise = enterprise_name

    def create(self, file_name, dumps, commit_message):
        """
        @param::file_name: desired name for file in repository
        @param::dumps: the byte codes of pipeline dumps
        @param::commit_message: Message for GitHub commit for versioning
        return None
        """ 
        if file_name == None:
            raise Exception('File name is required.')
        elif dumps == None:
            raise Exception('Dumps content is required.')
        elif commit_message == None:
            raise Exception('Commit Message is required.')
        try:
            self.repository.create_file(file_name, commit_message, dumps, branch=self.branch)
        except:
            raise Exception('Unsuccessful create of file')
    
    def read(self, file_name, version):
        """
        @param string::file_name: name of file user wants to read
        @param string::version: version number of file 
        return file content in bytes
        """
        if file_name == None:
            raise Exception('File name is required')
        if version != None and (version[0].lower() != 'v' or int(version[1:]) < 1):
            raise Exception('Incorrect Version Format')
        else:
            try:
                commits = self.repository.get_commits(path=file_name)
                total_commits = commits.totalCount
                if version == None:
                    ver_number = 0
                else:
                    ver_number = total_commits - int(version[1:])
                    if ver_number < 0:
                        ver_number = 0
                        print("Warning: The version number you entered does not exist.")
                version_commit = commits.get_page(0)[ver_number].sha
                contents = self.__get_commit_contents__(version_commit, file_name)
                return base64.b64decode(contents)
            except:
                raise Exception('Unsuccessful Read of File. Please Check Filename or Version.')
    
    def delete(self, file_name, commit_message):
        """
        @param::file_name: desired name for file to delete in repository
        return None if successful
        """ 
        if file_name == None:
            raise Exception('File name is required')
        elif commit_message == None:
            raise Exception('Commit message is required')
        else:
            try:    
                contents = self.repository.get_contents(file_name, ref=self.branch)
                self.repository.delete_file(contents.path, commit_message, contents.sha, self.branch)
            except:
                raise Exception('Unsuccessful deletion of file')

    def update(self, file_name, commit_message, dumps):
        """
        @param::dumps: the byte codes of pipeline dumps
        @param::file_name: desired name for file to delete in repository
        @param::commit_message: Message for GitHub commit for versioning
        return None if successful
        """ 
        if file_name == None:
            raise Exception('File name is required')
        elif commit_message == None:
            raise Exception('Commit message is required')
        elif dumps == None:
            raise Exception('Dumps content is required.')
        else:
            try:
                file = self.repository.get_contents(file_name)
                self.repository.update_file(file_name, commit_message, dumps, file.sha, self.branch)
            except:
                raise Exception('Unsuccessful update of file')

    def version_count(self, file_name):
        """
        @param string::file_name: name of file user wants to read
        return number of version
        """
        if file_name == None:
            raise Exception('File name is required')
        else:
            try:
                commits = self.repository.get_commits(path=file_name)
                total_commits = commits.totalCount
                return total_commits
            except:
                raise Exception('Unsuccessful Read of File. Please Check Filename or Version.')

    def __get_commit_contents__(self, sha, file_name):
        """
        @param string::sha: the commit sha key for the specific feature file version
        @param string::file_name: name of feature file we need content from
        return file content in bytes from specific commit provided
        """
        if self.enterprise == None:
            link = 'https://api.github.com'
        else:
            link = 'https://' + self.enterprise + '/api/v3'

        url = link + '/repos/' + self.username + '/' + self.repo_name + '/contents/' + \
                file_name + '?ref=' + sha

        headers = {
                "Authorization": "token " + self.token,
                "Accept": "application/vnd.github.v3+json"
            }

        r = requests.get(url, headers=headers)
        output = r.json()
        return output["content"]