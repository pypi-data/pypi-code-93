import click

from sdccli.cli.scanning.vulnerability import vulnerability
from sdccli.cli.scanning.image import image
from sdccli.cli.scanning.registry import registry
from sdccli.cli.scanning.repo import repo
from sdccli.cli.scanning.subscription import subscription
from sdccli.cli.scanning.policy import policy
from sdccli.cli.scanning.alert import alert
from sdccli.cli.scanning.runtime import runtime
from sdccli.cli.scanning.query import query
from sdccli.cli.scanning.cve_report import cve_report


@click.group(short_help='Scanning operations')
def scanning():
    pass


scanning.add_command(image)
scanning.add_command(registry)
scanning.add_command(repo)
scanning.add_command(subscription)
scanning.add_command(policy)
scanning.add_command(alert)
scanning.add_command(runtime)
scanning.add_command(query)
scanning.add_command(cve_report)
scanning.add_command(vulnerability)