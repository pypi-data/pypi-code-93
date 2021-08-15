import logging
import requests
from gitlab_client.config import GITLAB_BASE_URL_V4_DEFAULT
from gitlab_client.exceptions import JobError, MergeConflictError, MergeError, MergeRequestError, UnableToAcceptMR

logging.basicConfig(level=logging.INFO)


class Gitlab:
    """
    Return an instance of the given Gitlab project.

    Keyword arguments:
    project_id -- Id of the Gitlab project you want to instantiate and use. Can be found your repository's home page.
    access_token -- A personal access token generated from your Gitlab account.
                    See https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html on how to generate one.
    gitlab_base_url -- The base url where your repository is hosted.
    """
    def __init__(self, project_id, access_token, gitlab_base_url=GITLAB_BASE_URL_V4_DEFAULT, **kwargs):
        self.project_id = project_id
        self.access_token = access_token
        self.gitlab_base_url = gitlab_base_url
    
    # Branches
    def list_branches(self):
        response = self.__get(url="repository/branches")

        if response.ok:
            return response.json()
        
        return []


    def get_branch(self, branch_name):
        response = self.__get(url=f"repository/branches/{branch_name}")
        
        if response.ok:
            return response.json()
        else:
            error_message = response.json().get("message", response.reason)
            logging.error(f"Unable to get branch {branch_name}: {error_message}")


    def create_branch(self, branch_name, branch_from):
        data={"branch": branch_name, "ref": branch_from}
        response = self.__post(url="repository/branches", data=data)
        
        if response.ok:
            logging.info(f"Created branch: {response.json()['name']}")
        else:
            error_message = response.json().get("message", response.reason)
            logging.error(f"Unable to create branch {branch_name}: {error_message}")


    def delete_branch(self, branch_name):
        response = self.__delete(url=f"repository/branches/{branch_name}")
        
        if response.ok:
            logging.info(f"Deleted branch: {branch_name}")
        else:
            error_message = response.json().get("message", response.reason)
            logging.error(f"Unable to delete branch {branch_name}: {error_message}")
    
    # Tags
    def create_tag(self, tag_name, tag_on):
        data={"tag_name": tag_name, "ref": tag_on, "message": f"Automated release {tag_name}"}
        response = self.__post(url="repository/tags", data=data)
        
        if response.ok:
            logging.info(f"Created tag: {response.json()['name']}")
        else:
            error_message = response.json().get("message", response.reason)
            logging.error(f"Unable to create tag {tag_name}: {error_message}")


    def delete_tag(self, tag_name):
        response = self.__delete(url=f"repository/tags/{tag_name}")
        
        if response.ok:
            logging.info(f"Deleted tag: {tag_name}")
        else:
            error_message = response.json().get("message", response.reason)
            logging.error(f"Unable to delete tag {tag_name}: {error_message}")
    
    # Merge requests
    def get_merge_request(self, merge_request_iid):
        response = self.__get(url=f"merge_requests/{merge_request_iid}")

        json_response = response.json()
        if response.ok:
            return json_response
        else:
            error_message = json_response.get("message", response.reason)
            logging.error(f"Unable to get merge request: {error_message}")
            raise MergeRequestError
    
    
    def create_merge_request(self, source_branch, target_branch, title, **kwargs):
        data={"source_branch": source_branch, "target_branch": target_branch, "title": title, **kwargs}
        response = self.__post(url="merge_requests", data=data)
        
        json_response = response.json()
        if response.ok:
            logging.info(f"Created merge request: {json_response['iid']} - {json_response['title']}")
            return {
                "iid": json_response["iid"],
                "web_url": json_response["web_url"]
            }
        else:
            error_message = json_response.get("message", response.reason)
            logging.error(f"Unable to create merge request: {error_message}")
            raise MergeRequestError
    

    def get_or_create_merge_request(self, source_branch, target_branch):
        try:
            self.create_merge_request(source_branch, target_branch)
        except MergeRequestError:
            return {
                "iid": 123,
                "web_url": ""
            }


    def delete_merge_request(self, merge_request_iid):
        response = self.__delete(url=f"merge_request/{merge_request_iid}")
        
        if response.ok:
            logging.info(f"Deleted merge request: {merge_request_iid}")
        else:
            error_message = response.json().get("message", response.reason)
            logging.error(f"Unable to delete merge request {merge_request_iid}: {error_message}")


    def accept_mr(self, merge_request_iid):
        response = self.__put(url=f"merge_requests/{merge_request_iid}/merge")
        
        json_response = response.json()
        if response.ok:
            logging.info(f"Accepted merge request: {json_response['iid']} - {json_response['title']}")
        else:
            error_message = json_response.get("message", response.reason)
            logging.error(f"Unable to accept merge request {merge_request_iid}: {error_message}")
            if response.status_code == 401:
                logging.error(f"Unable to accept merge request because you don't have permissions to accept this merge request.")
                raise PermissionError
            elif response.status_code == 405:
                logging.error(f"Unable to accept merge request because it is either a Draft, Closed, Pipeline Pending Completion, or Failed while requiring Success.")
                raise UnableToAcceptMR
            elif response.status_code == 406:
                logging.error(f"Unable to accept merge request because of conflicts.")
                raise MergeConflictError
            raise MergeError
    
    # Pipelines
    def list_merge_request_pipelines(self, merge_request_iid):
        response = self.__get(url=f"merge_requests/{merge_request_iid}/pipelines")

        json_response = response.json()
        if response.ok:
            return json_response
        else:
            error_message = json_response.get("message", response.reason)
            logging.error(f"Unable to get pipelines for merge request {merge_request_iid}: {error_message}")
    

    def list_pipeline_jobs(self, pipeline_id, scopes=[]):
        params = {
            "scope[]": scopes
        }
        response = self.__get(url=f"pipelines/{pipeline_id}/jobs", params=params)
        
        json_response = response.json()
        if response.ok:
            return json_response
        else:
            error_message = json_response.get("message", response.reason)
            logging.error(f"Unable to get jobs for pipeline {pipeline_id}: {error_message}")
    
    def get_next_pipeline_job(self, pipeline_id):
        manual_pipeline_jobs = self.list_pipeline_jobs(pipeline_id, scopes=["manual"])
        
        return manual_pipeline_jobs[-1] if manual_pipeline_jobs else []
    
    
    def play_job(self,  job_id):
        response = self.__post(url=f"jobs/{job_id}/play")

        json_response = response.json()
        if response.ok:
            logging.info(f"Running job: {json_response['id']} - {json_response['name']}")
        else:
            error_message = json_response.get("message", response.reason)
            logging.error(f"Unable to play job {job_id}: {error_message}")
            raise JobError
    
    
    def __get(self, url, params={}):
        response = requests.get(
            f"{self.gitlab_base_url}/projects/{self.project_id}/{url}",
            headers={"PRIVATE-TOKEN": self.access_token},
            params=params
        )

        return response
    
    def __put(self, url, data={}):
        response = requests.put(
            f"{self.gitlab_base_url}/projects/{self.project_id}/{url}",
            headers={"PRIVATE-TOKEN": self.access_token},
            data=data
        )

        return response
    
    def __post(self, url, data={}):
        response = requests.post(
            f"{self.gitlab_base_url}/projects/{self.project_id}/{url}",
            headers={"PRIVATE-TOKEN": self.access_token},
            data=data
        )

        return response
    
    def __delete(self, url):
        response = requests.delete(
            f"{self.gitlab_base_url}/projects/{self.project_id}/{url}",
            headers={"PRIVATE-TOKEN": self.access_token}
        )

        return response
