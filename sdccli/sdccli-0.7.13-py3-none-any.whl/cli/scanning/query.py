import click
import json
import sys
from prettytable import PrettyTable, PLAIN_COLUMNS


@click.group(short_help='Query operations')
def query():
    pass


@query.command(name='images-by-vulnerability', short_help="Search system for images with the given vulnerability ID present")
@click.argument('vulnerability_id', nargs=1)
@click.option('--namespace', help="Filter results to images with vulnerable packages in the given namespace (e.g. debian:9)")
@click.option('--package', help="Filter results to images with the given vulnerable package name (e.g. sed)")
@click.option('--severity', help="Filter results to images with the given vulnerability severity (e.g. Medium)")
@click.option('--vendor_only', is_flag=True, help="Only show images with vulnerabilities explicitly deemed applicable by upstream OS vendor, if present")
@click.pass_obj
def images_by_vulnerability(cnf, vulnerability_id, namespace, package, severity, vendor_only):
    """
    VULNERABILITY_ID: Search for images vulnerable to this vulnerability ID (e.g. CVE-1999-0001)
    """
    ok, res = cnf.sdscanning.query_images_by_vulnerability(
        vulnerability_id,
        namespace=namespace,
        package=package,
        severity=severity,
        vendor_only=vendor_only)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_vulns(res['images'])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@query.command(name='images-by-package', short_help="Search system for images with the given package installed")
@click.argument('name', nargs=1)
@click.option('--version', help="Filter results to only packages with given version (e.g. 4.4-1)")
@click.option('--package-type', help="Filter results to only packages of given type (e.g. dpkg)")
@click.pass_obj
def images_by_package(cnf, name, version, package_type):
    """
    NAME: Search for images with this package name (e.g. sed)
    """
    ok, res = cnf.sdscanning.query_images_by_package(
        name,
        version=version,
        package_type=package_type)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_package(res['images'])
    else:
        print("Error: " + str(res))
        sys.exit(1)


def _print_vulns(images):
    header = ['Full Tag', 'Severity', 'Package', 'Package Type', 'Namespace', 'Digest']
    t = PrettyTable(header)
    t.set_style(PLAIN_COLUMNS)
    t.align = 'l'

    for image in images:
        for tag in image.get('image', {}).get('tag_history', []):
            for package in image.get('vulnerable_packages', []):
                row = [
                    tag.get('fulltag', "N/A"),
                    package.get('severity', "N/A"),
                    "{}-{}".format(package.get("name"), package.get("version")),
                    package.get("type"),
                    package.get('namespace', "N/A"),
                    image.get('image', {}).get('imageDigest', "N/A")]
                t.add_row(row)
    print(t.get_string(sortby='Full Tag'))


def _print_package(images):
    header = ['Full Tag', 'Package', 'Package Type', 'Digest']
    t = PrettyTable(header)
    t.set_style(PLAIN_COLUMNS)
    t.align = 'l'

    for image in images:
        for tag in image.get('image', {}).get('tag_history', []):
            for package in image.get('packages', []):
                row = [
                    tag.get('fulltag', "N/A"),
                    "{}-{}".format(package.get("name"), package.get("version")),
                    package.get("type"),
                    image.get('image', {}).get('imageDigest', "N/A")]
                t.add_row(row)
    print(t.get_string(sortby='Full Tag'))
