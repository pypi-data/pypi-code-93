import dateutil.parser
from sdcclient import SdScanningClient


def add_scanning_image(scanning: SdScanningClient, input_image, force, dockerfile, annotations, autosubscribe):
    ok, res = scanning.add_image(
        input_image,
        force=force,
        dockerfile=dockerfile,
        annotations=annotations,
        autosubscribe=autosubscribe)

    if not ok:
        raise Exception(res)

    return res


def list_scanning_images(scanning: SdScanningClient, show_all=True):
    ok, images = scanning.list_images()
    if not ok:
        raise Exception(images)

    if not show_all:
        images = _get_latest_image_records(images)
    return images


def _get_latest_image_records(images):
    latest_tag_details = {}
    latest_records = {}
    for image_record in images:
        for image_detail in image_record['image_detail']:
            fulltag = image_detail['fulltag']
            tagts = dateutil.parser.parse(image_detail['created_at'])
            if fulltag not in latest_tag_details:
                latest_tag_details[fulltag] = image_detail
                latest_records[fulltag] = image_record
            else:
                lasttagts = dateutil.parser.parse(latest_tag_details[fulltag]['created_at'])
                if tagts >= lasttagts:
                    latest_tag_details[fulltag] = image_detail
                    latest_records[fulltag] = image_record

    return list(latest_records.values())


def get_image_from_digest_id_or_repo(scanning: SdScanningClient, input_image, show_history):
    ok, res = scanning.get_image(input_image, show_history)
    if not ok:
        raise Exception(res)

    return res[0]


def query_image_content(scanning: SdScanningClient, input_image, content_type):
    supported_content_types = ["os", "npm", "gem", "files", "java", "python", "all", "all+files"]
    content_type = content_type.lower()

    if content_type not in supported_content_types:
        raise ValueError(f"Incorrect content type provided '{content_type}', must be one of: {supported_content_types}")

    if content_type not in ["all", "all+files"]:
        ok, res = scanning.query_image_content(input_image, content_type)
        if not ok:
            raise Exception(res)

        return res

    if content_type == "all":
        result = {"content": [], "content_type": "all"}

        for type in ["os", "npm", "gem", "java", "python"]:
            result["content"].append(query_image_content(scanning, input_image, type))

        return result

    if content_type == "all+files":
        result = {"content": [], "content_type": "all+files"}

        for type in ["os", "npm", "gem", "java", "python", "files"]:
            result["content"].append(query_image_content(scanning, input_image, type))

        return result

    raise Exception("unreachable code reached! report this to the CLI maintainers")


def query_image_metadata(scanning: SdScanningClient, input_image, metadata_type):
    if metadata_type not in ["manifest", "dockerfile", "docker_history"]:
        raise ValueError(
            "Incorrect metadata type provided 'foo', must be one of: [manifest, dockerfile, docker_history]")
    ok, res = scanning.query_image_metadata(input_image, metadata_type)


def query_image_vuln(scanning: SdScanningClient, input_image, vuln_type="all", vendor_only=True):
    if not vuln_type in ["os", "non-os", "all"]:
        raise ValueError("Incorrect vulnerability type provided, must be one of: [os, non-os, all]")

    ok, res = scanning.query_image_vuln(input_image, vuln_type, vendor_only=vendor_only)
    if not ok:
        raise Exception(res)

    return res


def get_image_scanning_results(scanning: SdScanningClient, input_image, policy):
    ok, res = scanning.get_image_scanning_results(input_image, policy)
    if not ok:
        raise Exception(res)
    return res


def get_pdf_report(scanning: SdScanningClient, input_image, tag, date):
    ok, res = scanning.get_pdf_report(
        input_image,
        tag=tag,
        date=date
    )
    if not ok:
        raise Exception(res)

    return res
