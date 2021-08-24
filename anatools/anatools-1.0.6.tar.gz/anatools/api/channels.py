"""
Channels API calls.
"""

def getChannels(self, organizationId=None, workspaceId=None, channelId=None, verbose=False):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getChannels",
            "variables": {
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "channelId": channelId
            },
            "query": """query 
                getChannels($organizationId: String, $workspaceId: String, $channelId: String) {
                    getChannels(organizationId: $organizationId, workspaceId: $workspaceId, channelId: $channelId) {
                        channelId
                        organizationId
                        name
                        updatedAt
                    }
                }"""})
    return self.errorhandler(response, "getChannels")


def getManagedChannels(self, organizationId, channelId=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getManagedChannels",
            "variables": {
                "organizationId": organizationId,
                "channelId": channelId
            },
            "query": """query 
                getManagedChannels($organizationId: String, $channelId: String) {
                    getManagedChannels(organizationId: $organizationId, channelId: $channelId) {
                        channelId
                        organizationId
                        name
                        instanceType
                        volumes
                        timeout
                        createdAt
                        updatedAt
                        organizations {
                            organizationId
                            name
                        }
                    }
                }"""})
    return self.errorhandler(response, "getManagedChannels")


def createManagedChannel(self, organizationId, name, dataVolumes=None, instanceType=None, timeout=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createManagedChannel",
            "variables": {
                "organizationId": organizationId,
                "name": name,
                "dataVolumes": dataVolumes,
                "instanceType": instanceType,
                "timeout": timeout
            },
            "query": """mutation 
                createManagedChannel($organizationId: String!, $name: String!, $dataVolumes: [String], $instanceType: String, $timeout: Int) {
                    createManagedChannel(organizationId: $organizationId, name: $name, dataVolumes: $dataVolumes, instanceType: $instanceType, timeout: $timeout)
                }"""})
    return self.errorhandler(response, "createManagedChannel")


def createManagedVolume(self, organizationId, name):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createManagedVolume",
            "variables": {
                "organizationId": organizationId,
                "name": name
            },
            "query": """mutation 
                createManagedVolume($organizationId: String!, $name: String!) {
                    createManagedVolume(organizationId: $organizationId, name: $name)
                }"""})
    return self.errorhandler(response, "createManagedVolume")


def addChannelOrganization(self, channelId, organizationId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "addChannelOrganization",
            "variables": {
                "channelId": channelId,
                "organizationId": organizationId
            },
            "query": """mutation 
                addChannelOrganization($channelId: String!, $organizationId: String!) {
                    addChannelOrganization(channelId: $channelId, organizationId: $organizationId)
                }"""})
    return self.errorhandler(response, "addChannelOrganization")


def removeChannelOrganization(self, channelId, organizationId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "removeChannelOrganization",
            "variables": {
                "channelId": channelId,
                "organizationId": organizationId
            },
            "query": """mutation 
                removeChannelOrganization($channelId: String!, $organizationId: String!) {
                    removeChannelOrganization(channelId: $channelId, organizationId: $organizationId)
                }"""})
    return self.errorhandler(response, "removeChannelOrganization")


def registerDocker(self, channelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "registerDocker",
            "variables": {
                "channelId": channelId 
            },
            "query": """mutation 
                registerDocker($channelId: String!) {
                    registerDocker(channelId: $channelId)
                }"""})
    return self.errorhandler(response, "registerDocker")


def registerData(self, package, key):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "registerData",
            "variables": {
                "package": package,
                "key": key 
            },
            "query": """mutation 
                registerData($package: String!, $key: String!) {
                    registerData(package: $package, key: $key)
                }"""})
    return self.errorhandler(response, "registerData")


def registerChannel(self, channelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "registerManagedChannel",
            "variables": {
                "channelId": channelId
            },
            "query": """mutation 
                registerManagedChannel($channelId: String!) {
                    registerManagedChannel(channelId: $channelId)
                }"""})
    return self.errorhandler(response, "registerManagedChannel")


def deployChannel(self, channelId, environment):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deployManagedChannel",
            "variables": {
                "channelId": channelId,
                "environment": environment
            },
            "query": """mutation 
                deployManagedChannel($channelId: String!, $environment: String!) {
                    deployManagedChannel(channelId: $channelId, environment: $environment)
                }"""})
    return self.errorhandler(response, "deployManagedChannel")

