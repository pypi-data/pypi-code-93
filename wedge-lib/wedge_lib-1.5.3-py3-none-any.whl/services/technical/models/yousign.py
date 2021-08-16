from dataclasses import dataclass, field
from w.mixins.dataclasses_mixin import DataclassMixin

default_subject = "Hey! Vous êtes invité à signer un document"
default_message = (
    'Bonjour <tag data-tag-type="string" '
    'data-tag-name="recipient.firstname"></tag> <tag '
    'data-tag-type="string" data-tag-name="recipient.lastname"></tag>,'
    "<br><br> Vous êtes invité à signer un document, veuillez cliquer "
    'sur le bouton suivant pour le lire :<br><br><tag data-tag-type="button" '
    'data-tag-name="url" data-tag-title="Accéder au contrat">Accéder '
    "au document</tag>"
)


@dataclass
class YouSignMail(DataclassMixin):
    subject: str = field(default_factory=lambda: default_subject)
    message: str = field(default_factory=lambda: default_message)
    to: list = field(default_factory=lambda: ["@member"])


@dataclass
class YouSignRequest(DataclassMixin):
    procedure_name: str
    procedure_desc: str
    filename: str
    member_firstname: str
    member_lastname: str
    member_email: str
    member_phone: str
    file_signature_position: str
    webhook_url: str
    member_started_mail: YouSignMail = field(default_factory=YouSignMail)

    def get_procedure_payload(self, file_id):
        return {
            "name": self.procedure_name,
            "description": self.procedure_desc,
            "members": [
                {
                    "firstname": self.member_firstname,
                    "lastname": self.member_lastname,
                    "email": self.member_email,
                    "phone": self.member_phone,
                    "fileObjects": [
                        {
                            "file": file_id,
                            "page": 1,
                            "position": self.file_signature_position,
                        }
                    ],
                }
            ],
            "config": {
                "email": {"member.started": [self.member_started_mail.to_dict()]},
                "webhook": {
                    "member.finished": [
                        {
                            "url": self.webhook_url,
                            "method": "POST",
                        }
                    ]
                },
            },
        }
