import copy


class ArtifactEmulator:
    def __init__(self, ctx, base_url):
        self._ctx = ctx
        self._artifacts = {}
        self._files = {}
        self._base_url = base_url

    def create(self, variables):
        collection_name = variables["artifactCollectionNames"][0]
        state = "PENDING"
        aliases = []
        latest = None
        art_id = variables.get("digest", "")

        # Find most recent artifact
        versions = self._artifacts.get(collection_name)
        if versions:
            last_version = versions[-1]
            latest = {"id": last_version["digest"], "versionIndex": len(versions) - 1}
        art_seq = {"id": art_id, "latestArtifact": latest}

        art_data = {
            "id": art_id,
            "digest": "abc123",
            "state": state,
            "labels": [],
            "aliases": aliases,
            "artifactSequence": art_seq,
        }

        response = {"data": {"createArtifact": {"artifact": copy.deepcopy(art_data)}}}

        # save in artifact emu object
        art_seq["name"] = collection_name
        art_data["artifactSequence"] = art_seq
        art_data["state"] = "COMMITTED"
        art_type = variables.get("artifactTypeName")
        if art_type:
            art_data["artifactType"] = {"id": 1, "name": art_type}
        self._artifacts.setdefault(collection_name, []).append(copy.deepcopy(art_data))

        # save in context
        self._ctx["artifacts_created"].setdefault(collection_name, {})
        self._ctx["artifacts_created"][collection_name].setdefault("num", 0)
        self._ctx["artifacts_created"][collection_name]["num"] += 1
        if art_type:
            self._ctx["artifacts_created"][collection_name]["type"] = art_type

        return response

    def create_files(self, variables):
        base_url = self._base_url
        response = {
            "data": {
                "createArtifactFiles": {
                    "files": {
                        "edges": [
                            {
                                "node": {
                                    "id": idx,
                                    "name": af["name"],
                                    "displayName": af["name"],
                                    "uploadUrl": f"{base_url}/storage?file={af['name']}&id={af['artifactID']}",
                                    "uploadHeaders": [],
                                    "artifact": {"id": af["artifactID"]},
                                }
                                for idx, af in enumerate(variables["artifactFiles"])
                            },
                        ],
                    },
                },
            },
        }
        return response

    def query(self, variables):
        art_name = variables["name"]
        collection_name, version = art_name.split(":", 1)
        artifact = None
        artifacts = self._artifacts.get(collection_name)
        if artifacts:
            if version == "latest":
                version_num = len(artifacts)
            else:
                assert version.startswith("v")
                version_num = int(version[1:])
            artifact = artifacts[version_num - 1]
            # TODO: add alias info?
        response = {"data": {"project": {"artifact": artifact}}}
        print("RESP=====", response)
        return response

    def file(self, entity, digest):
        # TODO?
        return "ARTIFACT %s" % digest, 200

    def storage(self, request):
        fname = request.args.get("file")
        if request.method == "PUT":
            data = request.get_data(as_text=True)
            self._files.setdefault(fname, "")
            # TODO: extend? instead of overwrite, possible to differentiate wandb_manifest.json artifactid?
            self._files[fname] = data
        data = ""
        if request.method == "GET":
            data = self._files[fname]
        return data, 200
