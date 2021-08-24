"""
Annotations API calls.
"""

def createAnnotation(self, workspaceId, datasetId, format, map):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "channelId": datasetId,
                "format": format,
                "map": map
            },
            "query": """query 
                createAnnotation($workspaceId: String!, $datasetId: String!, $format: String!, $map: String!) {
                    createAnnotation(workspaceId: $workspaceId, datasetId: $datasetId, format: $format, map: $map)
                }"""})
    return self.errorhandler(response, "createAnnotation")


def downloadAnnotation(self, workspaceId, datasetId, annotationId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadAnnotation",
            "variables": {
                "workspaceId": workspaceId,
                "channelId": datasetId,
                "format": annotationId
            },
            "query": """query 
                downloadAnnotation($workspaceId: String!, $datasetId: String!, $annotationId: String!) {
                    downloadAnnotation(workspaceId: $workspaceId, datasetId: $datasetId, annotationId: $annotationId)
                }"""})
    return self.errorhandler(response, "downloadAnnotation")
