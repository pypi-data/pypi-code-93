from arpeggio.cleanpeg import prefix
import pulumi_azure_native.resources as resources

def resource_group(stem, props):
    rg = resources.ResourceGroup(
        f'rg-{stem}',
        resource_group_name=f'rg-{stem}',
        tags=props.tags,
        location=props.location,
    )
    return rg.name