""" Citrix ADC latest AWS-AMI Finder """

import click
import operator
import boto3

from . import CITRIX_AWS_PRODUCTS, AWS_REGIONS

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def get_latest_citrixadc_ami(version, product, region):
    product_id = CITRIX_AWS_PRODUCTS[product]
    ec2_client = boto3.client('ec2', region_name=region)
    filters = [
        {"Name": "name", "Values": ["*{version}*{product_id}*".format(version=version,product_id=product_id)]}
    ]
    response = ec2_client.describe_images( Filters=filters)
    try:
        ami = sorted(response['Images'], key=operator.itemgetter("CreationDate"), reverse=True)[0]["ImageId"]
    except IndexError:
        click.echo("AMI not available for region={region}, version={version} and product={product}".format(region=region, version=version, product=product))
    else:
        return ami


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-r', '--region', type=click.Choice(AWS_REGIONS), help='AWS Region', show_default=True)
@click.option('-p', '--product', type=click.Choice(CITRIX_AWS_PRODUCTS.keys()), default='Citrix ADC VPX - Customer Licensed', help='Citrix Product Name', show_default=True)
@click.option('-v', '--version', type=click.Choice(['13.0']), default= '13.0', help='Citrix Product Version', show_default=True)
def main(region, product, version):
    latestami = get_latest_citrixadc_ami(version, product, region)
    click.echo(latestami)
