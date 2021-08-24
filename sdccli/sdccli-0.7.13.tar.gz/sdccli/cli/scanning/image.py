import sys

import click
import dateutil.parser

from sdccli import helpers
from sdccli.usecases.scanning import image as use_case


@click.group(short_help='Image operations')
def image():
    pass


@image.command(name='add', short_help="Add an image")
@click.argument('input_image', nargs=1)
@click.option('--force', is_flag=True, help="Force reanalysis of image")
@click.option('--dockerfile', type=click.Path(exists=True), metavar='<Dockerfile>',
              help="Submit image's dockerfile for analysis")
@click.option('--annotation', nargs=1, multiple=True)
@click.option('--noautosubscribe', is_flag=True,
              help="If set, instruct the engine to disable tag_update subscription for the added tag.")
@click.pass_obj
def add(cnf, input_image, force, dockerfile, annotation, noautosubscribe):
    """
    INPUT_IMAGE: Input image can be in the following formats: registry/repo:tag
    """
    dockerfile_contents = None
    if dockerfile:
        try:
            with open(dockerfile) as f:
                dockerfile_contents = f.read()
        except Exception as error:
            print("Error parsing dockerfile file (%s): %s" % (dockerfile, str(error)))
            sys.exit(1)

    annotations = helpers.annotation_arguments_to_map(annotation)
    annotations.update({"added-by": "sysdig-cli"})

    try:
        res = use_case.add_scanning_image(cnf.sdscanning,
                                          input_image,
                                          force=force,
                                          dockerfile=dockerfile_contents,
                                          annotations=annotations,
                                          autosubscribe=not noautosubscribe)
        cnf.formatter.format(res, "scanningImageAdded")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@image.command(name='list', short_help="List all images")
@click.option('--full', is_flag=True, help="Show full row output for each image")
@click.option('--show-all', is_flag=True,
              help="Show all images in the system instead of just the latest for a given tag")
@click.pass_obj
def imagelist(cnf, full, show_all):
    try:
        res = use_case.list_scanning_images(cnf.sdscanning, show_all=show_all)
        cnf.formatter.format(res, "scanningImageList")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@image.command(name='get', short_help="Get an image")
@click.argument('input_image', nargs=1)
@click.option('--show-history', is_flag=True,
              help="Show history of images that match the input image, if input image is of the form registry/repo:tag")
@click.pass_obj
def get(cnf, input_image, show_history):
    """
    INPUT_IMAGE: Input image can be in the following formats: Image Digest, ImageID or registry/repo:tag
    """
    try:
        res = use_case.get_image_from_digest_id_or_repo(cnf.sdscanning, input_image, show_history)
        cnf.formatter.format(res, "scanningImage")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@image.command(name='content', short_help="Get contents of image")
@click.argument('input_image', nargs=1)
@click.argument('content_type', nargs=1, required=True)
@click.pass_obj
def query_content(cnf, input_image, content_type):
    """
    INPUT_IMAGE: Input image can be in the following formats: Image Digest, ImageID or registry/repo:tag

    CONTENT_TYPE: The content type can be one of the following types:

      - os: Operating System Packages

      - files: Files

      - npm: Node.JS NPM Module

      - gem: Ruby GEM

      - python: Python modules

      - java: Java packages

      - all: includes [os, npm, gem, python, java] contents

      - all+files: includes [os, npm, gem, python, java, files] contents
    """
    try:
        res = use_case.query_image_content(cnf.sdscanning, input_image, content_type)
        cnf.formatter.format((res, content_type), "scanningQueryImage")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@image.command(name='metadata', short_help="Get metadata about an image")
@click.argument('input_image', nargs=1)
@click.argument('metadata_type', nargs=1, required=False)
@click.pass_obj
def query_metadata(cnf, input_image, metadata_type):
    """
    INPUT_IMAGE: Input image can be in the following formats: Image Digest, ImageID or registry/repo:tag

    METADATA_TYPE: The metadata type can be one of the types returned by running without a type specified
    """
    try:
        res = use_case.query_image_metadata(cnf.sdscanning, input_image, metadata_type)
        cnf.formatter.format((res, metadata_type), "scanningQueryImage")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@image.command(name='evaluation', short_help="Check latest policy evaluation for an image")
@click.option("--detail", is_flag=True, help="Show detailed policy evaluation report")
@click.option("--policy", help="Specify which POLICY to use for evaluate (defaults currently active policy)")
@click.argument('input_image', nargs=1)
@click.pass_obj
def check(cnf, input_image, detail, policy):
    """
    INPUT_IMAGE: Input image can be in the following formats: Image Digest, ImageID or registry/repo:tag
    """
    try:
        res = use_case.get_image_scanning_results(cnf.sdscanning, input_image, policy=policy)
        cnf.formatter.format((res, detail), "scanningEvaluationImage")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        if policy:
            print("Check if the image has been assigned to the provided policy")
        sys.exit(1)


@image.command(name='vuln', short_help="Get image vulnerabilities")
@click.argument('input_image', nargs=1)
@click.argument('vuln_type', nargs=1, default='all')
@click.option('--vendor-only', default=True, type=bool,
              help="Show only vulnerabilities marked by upstream vendor as applicable (default=True)")
@click.pass_obj
def query_vuln(cnf, input_image, vuln_type, vendor_only):
    """
    INPUT_IMAGE: Input image can be in the following formats: Image Digest, ImageID or registry/repo:tag

    VULN_TYPE: VULN_TYPE: Vulnerability type can be one of the following types:

      - os: CVE/distro vulnerabilities against operating system packages

      - non-os: NPM, Gem, Java Archive (jar, ear, war) and Python PIP CVEs

      - all: combination report containing both 'os' and 'non-os' vulnerability records (default)
    """
    try:
        res = use_case.query_image_vuln(cnf.sdscanning, input_image, vuln_type, vendor_only=vendor_only)
        cnf.formatter.format((res, vuln_type), "scanningVulnImage")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@image.command(name='pdf-report', short_help="Get the scan report for an image in pdf")
@click.option("--tag", help="Specify which TAG is evaluated for a given image ID or Image Digest")
@click.option("--date", help="Specify a date for the report")
@click.argument('input_image', nargs=1)
@click.argument('pdf_path', nargs=1)
@click.pass_obj
def pdf_report(cnf, input_image, pdf_path, tag, date):
    """
    INPUT_IMAGE: Input image can be in the following formats: Image Digest, ImageID or registry/repo:tag

    PDF_PATH: The name of the pdf that will be generated with the report
    """
    try:
        res = use_case.get_pdf_report(
            cnf.sdscanning,
            input_image,
            tag=tag,
            date=dateutil.parser.parse(date).strftime("%Y-%m-%dT%XZ") if date else None
        )
        with open(pdf_path, 'wb') as f:
            f.write(res)
        print("PDF %s saved" % pdf_path)

    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@image.command(name='del', short_help="Delete an image")
@click.argument('input_image', nargs=-1, required=True)
@click.option('--force', is_flag=True,
              help="Force deletion of image by cancelling any subscription/notification settings prior to image delete")
@click.pass_obj
def delete(cnf, input_image, force):
    """
    INPUT_IMAGE: Input image can be in the following formats: Image Digest, ImageID or registry/repo:tag
    """
    for image in input_image:
        ok, res = cnf.sdscanning.delete_image(image, force=force)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")
