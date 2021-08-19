from arpeggio.cleanpeg import prefix
import pulumi_azure_native.resources as resources

def hub_resource_group(stem):
    rg = resources.ResourceGroup(
        f'{preffix}{s}{stem}{s}rg',
        resource_group_name=f'{preffix}{s}{stem}{s}rg',
        tags=tags,
        location=location,
    )
    return rg.name

def spoke_resource_group(stem):
    rg = resources.ResourceGroup(
        f'{clientName}{s}{stem}{s}rg',
        resource_group_name=f'{clientName}{s}{stem}{s}rg',
        tags=tags,
        location=location,
    )
    return rg.name