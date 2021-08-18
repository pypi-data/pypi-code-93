import os
import json
import logging
import requests

CWD = os.path.dirname(os.path.realpath(__file__))
CURRENT_FILE = os.path.basename(__file__)
CURRENT_FILE_NAME, CURRENT_FILE_EXT = os.path.splitext(CURRENT_FILE)


class TeamsController:
    def __init__(self, webhook: str) -> None:
        self.webhook = webhook

    def createMessage(self, isError: bool, messageDetail: str, **kwargs) -> dict:
        """Fonction permettant la création et l'envoie de notifications dans un canal Teams.

        :param isError: Définit si la notification est une erreur ou pas
        :type isError: bool
        :param messageDetail: Détail du message
        :type messageDetail: str
        :return: Réponse suite à la tentative d'envoie de la notificaiton
        :rtype: dict
        """

        if isError:
            iconUrl = 'https://www.pngjoy.com/pngm/135/2736064_warning-symbol-error-png-transparent-png.png'
            color = 'f8333c'
        else:
            iconUrl = 'https://cdn.icon-icons.com/icons2/1506/PNG/512/emblemok_103757.png'
            color = '46c0c6'

        payloadDict = {
            "@type":
            "MessageCard",
            "@context":
            "http://schema.org/extensions",
            "themeColor":
            color,
            "summary":
            f"test",
            "sections": [{
                "activityTitle":
                kwargs.get('title', "Notification Auto"),
                "activitySubtitle":
                kwargs.get('subtitle', f"Envoyée depuis le fichier {CURRENT_FILE_NAME}"),
                "activityImage":
                iconUrl,
                "facts": [{
                    "name": "Owner",
                    "value": kwargs.get('owner', "Casper")
                }, {
                    "name": "Criticité",
                    "value": kwargs.get('criticiy', "Normale")
                }, {
                    "name": "Impact",
                    "value": kwargs.get('impacts', "n.c.")
                }, {
                    "name": "Origine (code source)",
                    "value": os.path.join(CWD, CURRENT_FILE)
                }, {
                    "name": "A prévenir",
                    "value": kwargs.get('personToWarn', "n.c.")
                }, {
                    "name": "Logs",
                    "value": kwargs.get('logsPath', "n.c.")
                }, {
                    "name": "RobotTask",
                    "value": kwargs.get('robotTaskName', 'Aucune Task')
                }],
                "markdown":
                True
            }, {
                "text": f"<blockquote>{messageDetail}</blockquote>"
            }]
        }

        payload = json.dumps(payloadDict)
        headers = {'Content-Type': 'text/plain'}
        try:
            requests.request("POST", self.webhook, headers=headers, data=payload)
            logging.info(f"Notification sent.")
            return {'response': 'success'}
        except:
            logging.error(f"Impossible to send Teams notification.", exc_info=True)
            return {'response': 'error'}