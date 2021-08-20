import logging
from datetime import datetime

from django.conf import settings
from django.db import transaction

from history.models.visitor import Visitor
from history.utils import get_ip
from isc_common.auth.http.LoginRequets import LoginRequest
from isc_common.auth.models.user import User
from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.models.progresses import ProgressesManager, Progresses
from tracker.models.messages_state import Messages_state

logger = logging.getLogger(__name__)


class LoginRequestEx(LoginRequest):
    def __init__(self, request):
        from django.forms import model_to_dict
        from reports.models.jasper_reports_users import Jasper_reports_users

        DSRequest.__init__(self, request)
        data = self.get_data()
        login = data.get('login', None)
        errorMessage = "Аутентификация не прошла :-("

        try:
            user = User.objects.get(username=login)

            if user.check_password(data.get('password', None)):
                ws_channel = f'{settings.WS_CHANNEL}_{login}'

                ip = get_ip(request)

                with transaction.atomic():
                    Visitor.objects.using('history').select_for_update()
                    # visitors_all = [visitor for visitor in Visitor.objects.using('history').filter(username=login)]
                    # if len(visitors_all) > 1:
                    #     Visitor.objects.using('history').filter(username=login).delete()

                    if settings.FREQUENCY_OF_POLLING_UNREAD_MESSAGES is None:
                        settings.FREQUENCY_OF_POLLING_UNREAD_MESSAGES = 1000 * 60 * 3

                    visitors = [visitor.ip_address for visitor in Visitor.objects.using('history').filter(username=login).exclude(ip_address=ip)]
                    if len(visitors) > 0:
                        ip_address = visitors[0]
                        if ip_address != ip:
                            self.response = dict(status=RPCResponseConstant.statusLoginIncorrect, errorMessage=f'Вход с логином "{login}" уже выполнен на {ip_address}')
                    else:

                        # location_ids_suffix = '_'.join(map(lambda x: str(x), location_ids)) if location_ids is not None else None
                        self.response = dict(
                            # dynDataSources=settings.DYNAMIC_CLASS.get_datasources(),
                            # ENABLE_FILE_VIEW=settings.ENABLE_FILE_VIEW,
                            # location_ids_suffix=location_ids_suffix,
                            captionUser=user.get_short_name,
                            chatInfo=LoginRequest.get_chats(user),
                            codeGroup="",
                            DEFAULT_TIMEOUT=settings.DEFAULT_TIMEOUT,
                            fio=user.get_short_name,
                            frequencyOfPollingUnreadMessages=settings.FREQUENCY_OF_POLLING_UNREAD_MESSAGES,
                            imageContentHost=settings.IMAGE_CONTENT_HOST,
                            imageContentPort=settings.IMAGE_CONTENT_PORT,
                            isAdmin=user.is_admin,
                            isDevelop=user.is_develop,
                            jsLogDebug=settings.JS_LOG_DEBUG if settings.JS_LOG_DEBUG == 1 else 0,
                            login=login,
                            message_state_delivered_id=Messages_state.message_state_delivered().id,
                            message_state_delivered_name=Messages_state.message_state_delivered().name,
                            message_state_new_id=Messages_state.message_state_new().id,
                            message_state_new_name=Messages_state.message_state_new().name,
                            message_state_not_readed_id=Messages_state.message_state_not_readed().id,
                            message_state_not_readed_name=Messages_state.message_state_not_readed().name,
                            message_state_readed_id=Messages_state.message_state_readed().id,
                            message_state_readed_name=Messages_state.message_state_readed().name,
                            progresses=[ProgressesManager.getRecord(item) for item in Progresses.objects.filter(user=user)],
                            status=RPCResponseConstant.statusSuccess,
                            user__color=user.color if user.color is not None and user.color != 'undefined' else 'black',
                            user_full_name=user.get_full_name,
                            user_short_name=user.get_short_name,
                            userId=user.id,
                            username=user.username,
                            ws_channel=ws_channel,
                            ws_host=settings.WS_HOST,
                            ws_port=settings.WS_PORT,
                            jasper_reports=[dict(
                                report=model_to_dict(item.report),
                                editor_identifier=item.editor_identifier,
                            ) for item in Jasper_reports_users.objects.filter(user=user)]
                        )
                        request.session['ws_channel'] = ws_channel
                        user.last_login = datetime.now()
                        user.save()

            else:
                self.response = dict(status=RPCResponseConstant.statusLoginIncorrect, errorMessage=errorMessage)

        except User.DoesNotExist:
            self.response = dict(status=RPCResponseConstant.statusLoginIncorrect, errorMessage=errorMessage)
