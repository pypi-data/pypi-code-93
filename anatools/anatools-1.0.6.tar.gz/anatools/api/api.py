class AnaAPI:

    def __init__(self, url, headers, verbose=False):
        import requests
        self.url = url
        self.headers = headers
        self.verbose = verbose
        self.session = requests.Session()

    def close(self):
        self.session.close()

    from .handlers      import errorhandler
    from .organizations import getOrganizations, createOrganization, deleteOrganization, editOrganization
    from .channels      import getChannels, getManagedChannels, addChannelOrganization, removeChannelOrganization, registerDocker, registerChannel, registerData, createManagedChannel, createManagedVolume, deployChannel
    from .members       import getMembers, addMember, removeMember, editMember, registerUser
    from .workspaces    import getWorkspaces, createWorkspace, deleteWorkspace, editWorkspace
    from .graphs        import getGraphs, createGraph, deleteGraph, editGraph, downloadGraph, getDefaultGraph
    from .datasets      import getDatasets, createDataset, deleteDataset, editDataset, downloadDataset
    from .limits        import getPlatformLimits, setPlatformLimit, getOrganizationLimits, setOrganizationLimit, getWorkspaceLimits, setWorkspaceLimit, getOrganizationUsage
