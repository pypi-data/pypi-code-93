from guillotina import app_settings
from guillotina.behaviors.attachment import IMultiAttachment

import json
import pytest

pytestmark = pytest.mark.asyncio


async def test_upload(custom_requester):
    async with custom_requester as requester:
        resp, status = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps(
                {
                    "id": "test-resource",
                    "@type": "Folder",
                    "@behaviors": [IMultiAttachment.__identifier__],
                }
            ),
        )
        assert status == 201
        uuid = resp["@uid"]

        binary = b"X" * 1024

        _, status = await requester(
            "PATCH",
            "/db/guillotina/test-resource/@upload/files/thumbnail",
            headers={"X-UPLOAD-FILENAME": "image.png"},
            data=binary,
        )
        assert status == 200

        resp, status = await requester(
            "GET",
            f"/db/guillotina/test-resource?include={IMultiAttachment.__identifier__}",
        )
        assert status == 200
        assert resp[IMultiAttachment.__identifier__]["files"]["thumbnail"] == {
            "filename": "image.png",
            "content_type": None,
            "size": 1024,
            "extension": "png",
            "md5": None,
        }

        resp, status = await requester(
            "GET", "/db/guillotina/test-resource/@download/files/thumbnail"
        )
        assert status == 200
        assert resp == binary

        upload_folder = app_settings["storage"]["upload_folder"]
        fs_path = f"{upload_folder}/guillotina/test-resource/{uuid}/image.png"
        with open(fs_path, "rb") as f:
            assert f.read() == binary

        resp, status = await requester(
            "DELETE", "/db/guillotina/test-resource/@delete/files/file1"
        )
        assert status == 404

        resp, status = await requester(
            "DELETE", "/db/guillotina/test-resource/@delete/files/thumbnail"
        )
        assert status == 200

        with pytest.raises(FileNotFoundError):
            with open(fs_path, "rb") as f:
                pass
