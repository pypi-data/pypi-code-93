from prettytable import PrettyTable, PLAIN_COLUMNS

from sdccli.printer import print_item, print_list


def formats():
    return {
        "scanningImage": _print_image,
        "scanningImageAdded": _print_image_added,
        "scanningImageList": _print_images,
        "scanningQueryImage": _print_query,
        "scanningVulnImage": _print_vuln,
        "scanningEvaluationImage": _print_evaluation,
    }


def _print_image_added(images):
    for image in images:
        _print_image(image)


def _print_image(image):
    image["fulltag"] = [d["fulltag"] for d in image['image_detail']]
    if 'image_content' in image and image['image_content']:
        image_content = image['image_content']
        if 'metadata' in image_content and image_content['metadata']:
            image_content_metadata = image_content['metadata']
            image['dockerfile_mode'] = str(image_content_metadata['dockerfile_mode'])
            image['distro'] = str(image_content_metadata['distro'])
            image['distro_version'] = str(image_content_metadata['distro_version'])
            image['size'] = str(image_content_metadata['image_size'])
            image['arch'] = str(image_content_metadata['arch'])
            image['layer_count'] = str(image_content_metadata['layer_count'])

    keys = ["imageDigest", "imageId", "parentDigest", "analysis_status", "image_type", "fulltag",
            "dockerfile_mode", "distro", "distro_version", "size", "arch", "layer_count", "annotations"]
    print_item(image, keys)


def _print_query(res):
    res, query_type = res
    if not query_type:
        for t in res:
            print("%s: available" % (t,))
        return
    if query_type in ['manifest', 'dockerfile', 'docker_history']:
        try:
            print(res.get('metadata', "").decode('base64'))
        except AttributeError:
            print("No metadata %s" % (query_type,))
        return
    if "content" not in res:
        print("No content")
        return

    content = res["content"]
    keys = {
        'os': ['package', 'version', 'license'],
        'files': ['filename', 'size'],
        'npm': ['package', 'version', 'location'],
        'gem': ['package', 'version', 'location'],
        'python': ['package', 'version', 'location'],
        'java': ['package', 'specification-version', 'implementation-version', 'location']
    }
    if query_type in keys:
        print_list(content, keys[query_type])
    elif query_type in ['all', 'all+files']:
        for elem in content:
            content_type = elem["content_type"]
            print(f"# {content_type}:")
            _print_query((elem, content_type))
    else:
        print_list(content, content[0].keys())


def _print_vuln(res):
    res, query_type = res
    if "vulnerabilities" not in res:
        print("No vulnerabilities")
        return

    vulnerabilities = res["vulnerabilities"]
    if query_type in ['os', 'non-os', 'all']:
        keys = ['vuln', 'package', 'severity', 'fix', 'url']
        print_list(vulnerabilities, keys)
    else:
        print_list(vulnerabilities, vulnerabilities[0].keys())


def _print_images(images):
    header = ['Full Tag', 'Image ID', 'Analysis Status', 'Image Digest']
    t = PrettyTable(header)
    t.set_style(PLAIN_COLUMNS)
    t.align = 'l'

    add_rows = []
    for image_record in images:
        for image_detail in image_record['image_detail']:
            imageId = image_detail.get('imageId', "None")
            fulltag = image_detail.get('registry', "None") + "/" + image_detail.get('repo',
                                                                                    "None") + ":" + image_detail.get(
                'tag', "None")

            row = [fulltag, imageId, image_record['analysis_status'], image_record['imageDigest']]
            if row not in add_rows:
                add_rows.append(row)
    for row in add_rows:
        t.add_row(row)
    print(t.get_string(sortby='Full Tag'))


def _print_evaluation(res):
    scan_info, detail = res
    print_item(scan_info, ["image_tag", "status", "image_digest", "image_id", "total_stop",
                           "total_warn", "last_evaluation", "policy_id", "policy_name"])

    if not detail:
        return

    if scan_info["warn_results"]:
        print("Warn results:")
        for warn_result in scan_info["warn_results"]:
            print(f"  - {warn_result}")

    if scan_info["stop_results"]:
        print("Stop results:")
        for stop_result in scan_info["stop_results"]:
            print(f"  x {stop_result}")
