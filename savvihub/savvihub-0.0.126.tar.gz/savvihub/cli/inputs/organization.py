import typer

from savvihub.api.exceptions import NotFoundAPIException
from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Context
from savvihub.cli.utils import get_default_organization


def organization_name_callback(ctx: Context, organization_name: str) -> str:
    if organization_name:
        try:
            ctx.authenticated_client.organization_read(organization_name)
        except NotFoundAPIException:
            raise ExitException('Organization not found.')
        return organization_name

    return (ctx.organization.name if ctx.organization
            else get_default_organization(ctx.authenticated_client).name)


organization_name_option = typer.Option(None, '--organization', callback=organization_name_callback,
                                        help='Override the default organization.')
