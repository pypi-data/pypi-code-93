from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_azure_native.storage as storage
import pulumi

def storage_account(stem, props, depends_on=None):
    sa = storage.StorageAccount(
        f'sa-{stem}',
        account_name=f'sa-{stem}',
        resource_group_name=props.resource_group_name,
        tags=props.tags,
        location=props.location,
        sku=storage.SkuArgs(name="Standard_GRS"),
        kind="Storage",
        minimum_tls_version="TLS1_2",
        allow_blob_public_access=False,
        opts=ResourceOptions(depends_on=depends_on)
    )

    # # Export the primary key of the Storage Account
    # bootstrap_sa_key = pulumi.Output.all(props.resource_group.name,sa.name).apply(lambda args: storage.list_storage_account_keys(
    #     resource_group_name=args[0],
    #     account_name=args[1]
    #     )).apply(lambda accountKeys: accountKeys.keys[0].value)

    return sa

def container(stem, props, sa_name, depends_on=None):
    blob_container = storage.BlobContainer(
        f'bc-{stem}', 
        container_name=f'bc-{stem}',
        account_name=sa_name, 
        resource_group_name=props.resource_group,
        opts=ResourceOptions(depends_on=depends_on)
    )
    return blob_container