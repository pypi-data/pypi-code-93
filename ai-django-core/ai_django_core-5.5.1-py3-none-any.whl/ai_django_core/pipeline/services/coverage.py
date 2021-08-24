import json
import os
import sys

import httpx


class CoverageService:
    """
    Class to be used in the gitlab-ci to ensure pipeline test coverage is not dropping on commit
    """
    TARGET_BRANCH = 'develop'

    def __init__(self) -> None:
        super().__init__()

        # Get ENV variables
        self.ci_pipeline_id: int = int(os.environ.get('CI_PIPELINE_ID'))
        self.base_api_url: str = os.environ.get('CI_API_V4_URL')
        self.token: str = os.environ.get('GITLAB_CI_COVERAGE_PIPELINE_TOKEN')
        self.project_id: int = int(os.environ.get('CI_PROJECT_ID'))
        self.pipeline_url = f'{self.base_api_url}/projects/{self.project_id}/pipelines?ref={self.TARGET_BRANCH}' \
                            f'&status=success&private_token={self.token}'

    def get_coverage_from_pipeline(self, pipeline_id: int) -> float:
        """
        Get coverage from given pipeline (by id)
        """
        pipeline_url = f'{self.base_api_url}/projects/{self.project_id}/pipelines/{pipeline_id}' \
                       f'?private_token={self.token}'
        response = httpx.get(pipeline_url)
        status_code = response.status_code

        if status_code != 200:
            raise ConnectionError(f'Call to pipeline api endpoint failed with status code {status_code}')

        coverage = json.loads(response.content).get('coverage', None)
        return 0.0 if coverage is None else float(coverage)

    def process(self):
        """
        Compare coverage from target branch (latest develop) with the current one.
        """
        # Get target pipeline id (from develop branch)
        response = httpx.get(self.pipeline_url)
        status_code = response.status_code

        # Ensure call did not go sideways
        if status_code != 200:
            raise ConnectionError(f'Call to global pipeline api endpoint failed with status code {status_code}')

        # Fetch target pipeline ID from content
        target_pipeline_id = json.loads(response.content)[0]['id']

        # Get coverage from target pipeline
        target_coverage = self.get_coverage_from_pipeline(target_pipeline_id)

        # Get coverage from target pipeline
        current_coverage = self.get_coverage_from_pipeline(self.ci_pipeline_id)

        # Compare target and current coverage
        if current_coverage < target_coverage:
            print(f'Coverage dropped from {target_coverage} to {current_coverage}.')
            sys.exit(1)
        else:
            print(f'Coverage changed from {target_coverage} to {current_coverage}.')
