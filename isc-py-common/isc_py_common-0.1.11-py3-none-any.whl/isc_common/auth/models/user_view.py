import logging

from isc_common.auth.models.user import User, UserManager

logger = logging.getLogger(__name__)


class UserView(User):
    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        managed = False
        db_table = 'isc_common_user_view'
