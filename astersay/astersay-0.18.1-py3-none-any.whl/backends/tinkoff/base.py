#
#  Copyright (c) 2021. Egor Demushin.
#  All rights reserved.
#  This file is distributed under the same license as the current project.
#
from astersay.backends.base import BaseBackend
from astersay.backends.tinkoff.token import TinkoffTokenManager


class TinkoffBaseBackend(BaseBackend):
    token_manager = None

    def set_token_manager(self, settings, force=False):
        """
        Устанавливает из любого экземпляра общий для основного класса менеджер
        токена.
        """
        if self.token_manager and not force:
            return self.token_manager
        tm = TinkoffTokenManager(**settings.tinkoff['auth'])
        TinkoffBaseBackend.token_manager = tm
        return tm
