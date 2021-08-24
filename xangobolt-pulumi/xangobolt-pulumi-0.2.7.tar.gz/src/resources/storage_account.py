from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_azure_native.storage as storage
import pulumi

def storage_account(stem, props, resource_group, provider=None, parent=None, depends_on=None):
    sa = storage.StorageAccount(
        f'sa-{stem}',
        account_name=f'sa-{stem}',
        resource_group_name= resource_group,
        tags=props.tags,
        location=props.location,
        sku=storage.SkuArgs(name="Standard_GRS"),
        kind="Storage",
        minimum_tls_version="TLS1_2",
        allow_blob_public_access=False,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sa

def container(stem, props, sa_name, resource_group, provider=None, parent=None, depends_on=None):
    blob_container = storage.BlobContainer(
        f'bc-{stem}', 
        container_name=f'bc-{stem}',
        account_name=sa_name, 
        resource_group_name=resource_group,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return blob_container