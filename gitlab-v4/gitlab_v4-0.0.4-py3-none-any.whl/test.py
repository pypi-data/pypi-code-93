from gitlab_client import Gitlab


client = Gitlab(
    access_token="AvBRFHiek-C4zNs63zF6",
    project_id="28351523",
    gitlab_base_url="https://gitlab.com/api/v4"
)

mrs = client.get_or_create_merge_request(
    source_branch="main",
    target_branch="stable",
    title="test get or create mr",
    labels="release,v0.0.0"
)

print(mrs)
