from typing import Any, Dict, List
import botocore.config


def sig_gather(hub) -> Dict[str, Any]:
    ...


def post_gather(hub, ctx) -> Dict[str, Any]:
    """
    TODO Sanitize these profiles and make sure they have everything needed
    https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html
    """
    profiles = ctx.ret or {}

    hub.log.info(f"Read {len(profiles)} profiles from {ctx.ref}")

    for name, profile in profiles.items():
        profiles[name] = _sanitize_profile(profile)

    return profiles


def _sanitize_profile(profile: Dict[str, str]) -> Dict[str, str]:
    region = profile.get("region") or profile.get("region_name")
    return {
        "region_name": _key_options(profile, ["region_name", "region", "location"]),
        "api_version": profile.get("api_version"),
        "verify": profile.get("verify"),
        "use_ssl": profile.get("use_ssl"),
        "endpoint_url": _key_options(profile, ["endpoint_url", "endpoint"]),
        "aws_access_key_id": _key_options(
            profile, ["aws_access_key_id", "key_id", "id"]
        ),
        "aws_session_token": _key_options(
            profile, ["aws_session_token", "session_token", "token", "key"]
        ),
        "config": botocore.config.Config(**profile.get("config", {})),
    }


def _key_options(d: Dict[str, Any], keys: List[str]):
    for key in keys:
        if key in d:
            return d[key]
    else:
        return None
