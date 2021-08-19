"""
Library routine to get volume information from BUDA
"""
import requests
from requests import Response


def fixOldHack(image_group_id: str) -> str:
    """
    Copied from volume-manifest-builder.
    :param image_group_id:
    :type image_group_id: str
    Some old image groups in eXist are encoded Innn, but their real name on disk is
    RID-nnnn. this detects their cases, and returns the disk folder they actually
    exist in. This is a gross hack, we should either fix the archive repository, or have the
    BUDA and/or eXist APIs adjust for this.
    """
    pre, rest = image_group_id[0], image_group_id[1:]
    if pre == 'I' and rest.isdigit() and len(rest) == 4:
        suffix = rest
    else:
        suffix = image_group_id
    return suffix

def get_disk_volumes_in_work(work_rid: str) -> []:
    """
    BUDA LDS-PDI implementation
    :param: work_rid
    :return: list of dicts of 'vol_seq_in_work, vol_label' entries, where vol_label is the (potentially different)
    disk directory of an image group.
    """

    vol_info = []

    request_url: str = f'http://purl.bdrc.io/query/table/volumesForInstance'
    request_args = dict(R_RES=f"bdr:{work_rid}", format="json")

    # pattern from https://www.programcreek.com/python/example/68989/requests.HTTPError
    try:
        BUDA_vol_resp: Response = requests.get(request_url, request_args)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None
        else:
            raise

    vol_ids = BUDA_vol_resp.json()
    for vol_id in vol_ids['results']['bindings']:
        _vol_names = vol_id['volid']['value'].split('/')
        _vol_name = _vol_names[len(_vol_names) - 1]
        vol_info.append(dict(vol_seq_in_work=int(vol_id['volnum']['value']), vol_label=fixOldHack(_vol_name)))

    return vol_info
