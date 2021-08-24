import csv
import json
import sys
from datetime import timezone
from multiprocessing.pool import ThreadPool

import click
import dateutil

COLUMN_MAP = {
    "image": None,
    "type": None,
    "imageDigest": None,
    "feed": "feed",
    "feed_group": "feed_group",
    "fix": "fix",
    "package": "package",
    "package_cpe": "package_cpe",
    "package_name": "package_name",
    "package_path": "package_path",
    "package_type": "package_type",
    "package_version": "package_version",
    "severity": "severity",
    "url": "url",
    "vuln": "vuln",
    "whitelisted": None,
    "cvss_v2_base_score": ("nvd_data", 0, "cvss_v2", "base_score"),
    "cvss_v2_exploitability_score": ("nvd_data", 0, "cvss_v2", "exploitability_score"),
    "cvss_v2_impact_score": ("nvd_data", 0, "cvss_v2", "impact_score"),
    "cvss_v3_base_score": ("nvd_data", 0, "cvss_v3", "base_score"),
    "cvss_v3_exploitability_score": ("nvd_data", 0, "cvss_v3", "exploitability_score"),
    "cvss_v3_impact_score": ("nvd_data", 0, "cvss_v3", "impact_score"),
}


# TODO: Merging or sorting?
# TODO: Multiple digests for same tag! Or multiple tags for each image. Causing duplicates. Probably we could save time recovering by digest, and in fact I am not sure if we are recovering issues correctly.

@click.command(name='cve-report', short_help="(DEPRECATED Use 'sdc-cli scanning vulnerability report') Get a CVE report")
@click.option("--runtime", help="Generate CVE report for runtime images only", type=bool)
@click.option("--scope",
              help="Prefix to filter the images in the report. i.e. 'gcr.io/sysdig/sysdig-agent:latest' or 'docker.io/'")
@click.option("--date",
              help="Specify a date for the report. Only images created after this date will be included in the report. Use format YYYY-MM-DD or \"YYYY-MM-DD HH:MM\"")
@click.option("--columns", help="List of comma-separated colums. Available columns: %s" % ", ".join(COLUMN_MAP),
              default="image,imageDigest,type,vuln,whitelisted,package_path,fix,cvss_v3_base_score,cvss_v2_base_score,severity,package,url",
              show_default=True)
@click.argument('report_path', nargs=1, required=False)
@click.pass_obj
def cve_report(cnf, runtime, scope, date, columns, report_path):
    """
    (DEPRECATED Use 'sdc-cli scanning vulnerability report')
    """
    print("WARNING. This option has been deprecated, please use 'sdc-cli scanning vulnerability report'")
    if not cnf.json and not report_path:
        print("Missing REPORT_PATH argument")
        sys.exit(1)

    parsed_date = None
    try:
        if date:
            parsed_date = dateutil.parser.parse(date).replace(tzinfo=timezone.utc)
    except dateutil.parser.ParserError as e:
        print("Error parsing date:\n%s" % e)
        sys.exit(1)

    column_list = columns.split(",")
    for col in column_list:
        if col not in COLUMN_MAP:
            print("Invalid column: %s" % col)
            sys.exit(1)

    if runtime:
        if parsed_date:
            print("Date filtering not supported for --runtime")
            sys.exit(1)
        images = get_runtime_images(cnf)
        if len(images) == 0:
            print("Warning: no runtime images detected, the report will be empty")
    else:
        images = get_all_images(cnf)

    filtered_images = filter_images(images, scope, parsed_date)

    cve_whitelist = get_whitelisted_cves(cnf)

    cves = []

    for idx, (ok, image_cves) in enumerate(
            ThreadPool().map(lambda img:
                             add_cves_for(cnf, img, cve_whitelist, column_list), filtered_images)
    ):
        if not ok:
            return print_error(cnf, image_cves, exit_app=False)

        cves.extend(image_cves)

    if cnf.json:
        print(json.dumps(cves, indent=4))
    else:
        export_cvs_report(report_path, cves, column_list)
        print("Report %s saved" % report_path)


def get_all_images(cnf):
    images = []
    ok, res = cnf.sdscanning.list_images()
    if not ok:
        return print_error(cnf, res)
    for image in res:
        if image["analysis_status"] != "analyzed":
            continue
        for image in image["image_detail"]:
            images.append(image)
    return images


def get_runtime_images(cnf):
    images = []
    ok, res = cnf.sdscanning.list_runtime()
    if not ok:
        return print_error(cnf, res)

    for image in res["images"]:
        if image["analysisStatus"] != "analyzed":
            continue
        images.append({
            "imageDigest": image["digest"],
            "fulldigest": image["repo"] + "@" + image["digest"],
            "fulltag": image["repo"] + ":" + image["tag"]
        })
    return images


def get_whitelisted_cves(cnf):
    whitelisted_cves = set([])
    ok, bundles = cnf.sdscanning.list_vulnerability_exception_bundles()
    if not ok:
        return print_error(cnf, bundles)

    for bundle in bundles:
        ok, res = cnf.sdscanning.get_vulnerability_exception_bundle(bundle=bundle["id"])
        if not ok:
            return print_error(cnf, res)
        for item in res["items"]:
            whitelisted_cves.add(item["trigger_id"])

    return whitelisted_cves


def export_cvs_report(report_path, cves, column_list):
    with open(report_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(column_list)
        for cve in cves:
            row = []
            for col in column_list:
                row.append(cve[col])
            writer.writerow(row)


def filter_images(images, scope, date):
    filtered_images = []
    for image in images:

        if scope and not image["fulltag"].startswith(scope):
            continue

        if date and "created_at" in image and dateutil.parser.parse(image["created_at"]) < date:
            continue

        filtered_images.append(image)

    return filtered_images


def print_error(cnf, res, exit_app=True):
    if cnf.json:
        print(json.dumps(res, indent=4))
        sys.exit(1)

    else:
        print("Error: " + str(res))
        if exit_app:
            sys.exit(1)


def add_cves_for(cnf, image_detail, cve_whitelist, column_list):
    if not cnf.json:
        print(f"Recovering vulnerability report for: {image_detail['fulltag']} ({image_detail['imageDigest']}) ")
    cves = []
    for vuln_type in ["os", "non-os"]:
        # Recovering by digest, as it makes more sense
        ok, res = cnf.sdscanning.query_image_vuln(image_detail["fulldigest"], vuln_type, vendor_only=True)
        if not ok:
            return False, res
        cves.extend(flatten_vuln_list(cnf, image_detail, vuln_type, cve_whitelist, column_list, res["vulnerabilities"]))

    return True, cves


def flatten_vuln_list(cnf, image_detail, vuln_type, cve_whitelist, column_list, vulnerabilities):
    flat_vulnerabilities = []
    for vuln in vulnerabilities:
        flat_vuln = {}
        for col in column_list:
            target = COLUMN_MAP[col]

            if col == "type":
                flat_vuln[col] = vuln_type
            elif col == "image":
                flat_vuln[col] = image_detail["fulltag"]
            elif col == "imageDigest":
                flat_vuln[col] = image_detail["imageDigest"]
            elif col == "whitelisted":
                flat_vuln[col] = vuln["vuln"] in cve_whitelist
            elif isinstance(target, str):
                flat_vuln[col] = vuln[target]
            elif isinstance(target, tuple):
                try:
                    value = vuln
                    for k in target:
                        value = value[k]
                except:
                    value = None
                flat_vuln[col] = value
        flat_vulnerabilities.append(flat_vuln)
    return flat_vulnerabilities
