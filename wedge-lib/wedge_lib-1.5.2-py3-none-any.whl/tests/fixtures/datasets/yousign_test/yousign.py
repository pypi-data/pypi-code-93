import os

from w.services.technical.models.yousign import YouSignRequest
from w.services.technical.yousign_service import YouSignService

YOUSIGN_API_URL = "https://staging-api.yousign.com"
YOUSIGN_API_KEY = "330fdd14a571dd22241ad8002f2ab545"

pdf = f"{os.path.dirname(os.path.abspath(__file__))}/../pdf/exemple_pdf.pdf"
data = {
    "procedure_name": "Test de création",
    "procedure_desc": "Un test pour valider le fonctionnement",
    "filename": pdf,
    "member_firstname": "François",
    "member_lastname": "Schneider",
    "member_email": "fr-schneider@orange.fr",
    "member_phone": "+33662344601",
}

yousign_request = YouSignRequest(**data)

if __name__ == "__main__":
    YouSignService.init(YOUSIGN_API_URL, YOUSIGN_API_KEY)
    member_id = YouSignService.create(yousign_request)
    print(f"member_id = {member_id}")

# /members/653285fa-0aee-44c2-a065-ee105b2090de
