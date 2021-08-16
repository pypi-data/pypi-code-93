def configuration():
    x = {
        "email": {
            "endpoint": "",
            "header": {
                "Authorization": "Basic c3NzOmZmZg==",
                "accept": "application/json",
                "content-type": "application/json",
                "x-myntra-client-id": "pretrpims",
                "x-myntra-idea-tenant" : "5"
            }
        },
        "slack": {
            "slack_url": "",
            "header": {
                "content-type": "application/json"
            }
        }
    }
    return x