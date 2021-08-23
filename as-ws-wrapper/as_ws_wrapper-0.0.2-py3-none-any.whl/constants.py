from decouple import config

USERNAME = config("IMOBANCO_AS_WS_USERNAME", default="")
"""Nome do usuário para autenticação"""

PASSWORD = config("IMOBANCO_AS_WS_PASSWORD", default="")
"""Token básico para autenticação"""
