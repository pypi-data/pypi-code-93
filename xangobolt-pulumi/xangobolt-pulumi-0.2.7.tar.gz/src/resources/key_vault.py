from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_azure_native.keyvault as keyvault

def vault(stem, props, resource_group, provider=None, parent=None, depends_on=None):
    kv = keyvault.Vault(
        f'kv-{stem}',
        vault_name=f'kv-{stem}',
        resource_group_name= resource_group,
        tags=props.tags,
        location=props.location,
        properties=keyvault.VaultPropertiesArgs(
            sku=keyvault.SkuArgs(
                family="A",
                name="standard"
            ),
            tenant_id=props.tenantId,
            ),
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return kv


def key(stem, props, vaultName, resource_group, provider=None, parent=None, depends_on=None):
    key = keyvault.Key(f'key-{stem}',
        key_name=f'key-{stem}',
        properties=keyvault.KeyPropertiesArgs(
            kty="RSA",
            key_size=2048
        ),
        resource_group_name=resource_group,
        vault_name=vaultName, 
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return key