from guillotina import configure

app_settings = {
    "cloud_storage": "guillotina_localstorage.interfaces.IDiskFileField",
    "storage": {"upload_folder": "/tmp"},
}


def includeme(root):
    """
    custom application initialization here
    """
    configure.scan("guillotina_localstorage.adapters")
    configure.scan("guillotina_localstorage.storage")
