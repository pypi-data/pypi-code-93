""" Модуль содержит все методы SDK для взаимодействия с API """

methods_dict = {'subscribe': {'command': 'subscribe',
                              'args': (),
                              'kwargs': {},
                              'test': False,
                              'description': 'Подписаться на обновления от QPI'},
                'unsubscribe': {'command': 'unsubscribe',
                                'args': (),
                                'kwargs': {},
                                'test': False,
                                'description': 'Отписаться от обновлений QPI'},
                'hello_world': {'command': 'hello_world',
                                'args': (),
                                'kwargs': {},
                                'test': False,
                                'description': 'Отпавить тестовую команду'},
                'auth_me': {'command': 'auth_me',
                            'args': (),
                            'kwargs': {},
                            'test': False,
                            'description': 'Отправить команду на аутентификацию QDK на QPI'},
                }

