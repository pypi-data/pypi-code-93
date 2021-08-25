from typing import Any, Dict, Optional, Tuple

from click import ClickException
from openapi_client.rest import ApiException

from anyscale.client.openapi_client.api.default_api import DefaultApi


def get_cloud_json_from_id(cloud_id: str, api_client: DefaultApi) -> Dict["str", Any]:
    try:
        cloud = api_client.get_cloud_api_v2_clouds_cloud_id_get(
            cloud_id=cloud_id
        ).result
    except ApiException:
        return {
            "error": {
                "cloud_id": cloud_id,
                "message": f"The cloud with id, {cloud_id} has been deleted. Please create a new cloud with `anyscale cloud setup`.",
            }
        }
    return {
        "id": cloud.id,
        "name": cloud.name,
        "provider": cloud.provider,
        "region": cloud.region,
        "credentials": cloud.credentials,
        "config": cloud.config,
    }


def get_cloud_id_and_name(
    api_client: DefaultApi,
    cloud_id: Optional[str] = None,
    cloud_name: Optional[str] = None,
) -> Tuple[str, str]:
    if cloud_id and cloud_name:
        raise ClickException(
            "Both '--cloud-id' and '--cloud-name' specified. Please only use one."
        )
    elif cloud_name:
        resp_get_cloud = api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post(
            cloud_name_options={"name": cloud_name}
        )
        cloud = resp_get_cloud.result
    elif cloud_id:
        resp_get_cloud = api_client.get_cloud_api_v2_clouds_cloud_id_get(
            cloud_id=cloud_id
        )

        cloud = resp_get_cloud.result
    else:
        try:
            clouds = api_client.list_clouds_api_v2_clouds_get().results
        except Exception as e:
            if (isinstance(e, ApiException) and e.status == 404) or (  # type: ignore
                isinstance(e, ClickException) and "Reason: 404" in str(e)
            ):
                # No clouds
                raise ClickException(
                    'There are no clouds assigned to your account. Please create a cloud using "anyscale cloud setup".'
                )
            raise e

        if len(clouds) == 0:
            # No clouds
            raise ClickException(
                'There are no clouds assigned to your account. Please create a cloud using "anyscale cloud setup".'
            )

        if len(clouds) > 1:
            raise ClickException(
                "Multiple clouds: {}\n"
                "Please specify the one you want to refer to using --cloud-name.".format(
                    [cloud.name for cloud in clouds]
                )
            )
        cloud = clouds[0]
    return cloud.id, cloud.name
