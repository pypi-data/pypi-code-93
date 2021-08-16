from abc import ABCMeta, abstractmethod

class NotificationController(metaclass=ABCMeta):
    @abstractmethod
    def _send_notification(self, data: dict):
        pass

    @abstractmethod
    def _process_data(self, **data):
        pass

    def notify(self, **data):
        self._process_data(**data)
        rsp = self._send_notification()
        return rsp


from NotificationServices.providers import _all_providers

def all_providers() -> list:
    return list(_all_providers.keys())

def get_notifier(provider_name: str) -> NotificationController:

    if provider_name in _all_providers:
        return _all_providers[provider_name]()


def notify(provider_name: str, **data):
    get_notifier(provider_name)
    return get_notifier(provider_name).notify(**data)

class ManageNotification:

    def slacknotify(self, subject, body, slack_url, data):
        if slack_url:
            content = []
            content.append({'message': subject, 'type': "subject"})
            content.append({'message':  body, 'type': 'plain_text'})
            if data['log_link']:
                content.append({
                    'message': f"{data['log_text']}, Click on button to download a file : " if data['log_text'] else 'Refer log file for more details, Click on button to download a file : ',
                    'type': 'link', 'url': data['log_link']})
            if data['file_link']:
                content.append({
                    'message': f"{data['file_text']} , Click on button to download a file : " if data['file_text'] else 'Processed uploaded file, Click on button to download a file : ',
                    'type': 'link', 'url': data['file_link']})
            notify(provider_name='slack', slack_url=slack_url, contents=content)
        return True


    def emailnotify(self, email_uidx, subject, body, slack_url, data,endpoint='http://hermes.stage.myntra.com/myntra-notification-service/platform/notification/v2/email/event/publishWithUidx'):
        if email_uidx:
            html_body = f"{body} <br> \n "
            if data['log_link']:
                html_body += f"<br> {data['log_text']}, Click on button to download a file : {data['log_link']} <br> \n " if data['log_text'] else f"<br> Refer log file for more details, Click on button to download a file : {data['log_link']} <br> \n "
            if data['file_link']:
                html_body += f"<br> {data['file_text']} , Click on button to download a file : {data['file_link']} <br> \n " if data['file_text'] else f"<br> Processed uploaded file, Click on button to download a file : {data['file_link']} <br> \n "
            html_body += f"<br/><br/><b>* You can also check the Slack channel <i><font color='green'> {slack_url}</font> </i>for all the latest and past update regarding simillar events."
            data = {
                'uidx' :  email_uidx,
                'subject' : subject,
                'html_body' : '<p>' + html_body + '</p>',
                'endpoint' : endpoint,
                'template_name' : 'PR_EXPORTMAIL'
            }
            notify(provider_name='email', **data)
        return True