CRM_PERFIL_ENDPOINT = {
    "perfis": {
        "resource": "backend/perfis/",
        "methods": ["GET"],
    }
}
CRM_OAUTH = {
    "oauth_token": {
        "resource": "backend/oauth-token/",
        "methods": ["POST"],
    }
}


CRM_LICENCA_ENDPOINT = {
    "licencas-list": {
        "resource": "backend/licencas/",
        "methods": ["GET"],
    },
    "licenca": {
        "resource": "backend/licencas/{codigo}",
        "methods": ["GET"],
    }
}
