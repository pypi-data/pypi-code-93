from slugify import slugify

from trifacta.constants import Recipe
from trifacta.util import tfrequests


def get_user_and_aws_config():
    user = tfrequests.get(url="/v4/people/current").json()
    conf = dict(tfrequests.get_config())
    awsConfig = None
    r = tfrequests.raw_get(url="/v4/awsConfigs/current", params={"limit": 1})
    if r.status_code == 200:
        data = r.json()
        if data:
            awsConfig = data
    return user, conf, awsConfig


def create_flow(flow_name):
    """
    @param flow_name: name of the generated flow
    @type flow_name: str
    @returns: (flow node id, flow name)
    """
    payload = {
        # "workspaceId": 1, ## do we need this param?  I'm not sure!
        "name": slugify(flow_name),
        "description": "python-generated flow",
    }
    resp = tfrequests.post(url="/v4/flows/", json=payload).json()
    return resp["id"], slugify(resp["name"])


def upload_dataset_to_flow(data_alias_tuple: tuple, flow_id: int):
    resp = tfrequests.upload(url=f'/v4/flows/{flow_id}/importAndAddDatasetToFlow',
                             filename=f'pyfacta_{data_alias_tuple[1]}',
                             file=data_alias_tuple[0].to_csv(index=False)).json()
    recipe = Recipe(resp['wrangledDatasetName'], resp['wrangledDatasetId'])
    return recipe


def get_flow_nodes(flow_id: int):
    flow_nodes = tfrequests.get(f"/v4/flows/{flow_id}?embed=flowNodes.recipe").json()['flowNodes']['data']
    return flow_nodes


def get_python_code(flow_id: int):
    response = tfrequests.post(
        f'/v4/outputObjects/{flow_id}/wrangleToPython',
        json={"orderedColumns": " "}
    ).json()
    return response['pythonScript']
