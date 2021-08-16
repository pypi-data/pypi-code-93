""" Модуль содержит настройки gravityRecorder """


# Разрешенные для отправки клиентам таблицы из базы данных по запросу get_wdb_info
# Table_name - имя таблицы. Except_columns - поля, которые отправляться не будут


users_table = 'users'
clients_table = 'clients'
trash_cats_table = 'trash_cats'
trash_types_table = 'trash_types'
pol_owners_table = 'duo_pol_owners'
auto_table = 'auto'

send_allowed_table_rules = {users_table: {'table_name': users_table,
                                          'except_columns': ['password']},
                            clients_table: {'table_name': clients_table,
                                            'except_columns': []},
                            trash_cats_table: {'table_name': trash_cats_table,
                                               'except_columns': []},
                            trash_types_table: {'table_name': trash_types_table,
                                                'except_columns': []},
                            pol_owners_table: {'table_name': pol_owners_table,
                                               'except_columns': ['password',
                                                                  'login']},
                            auto_table: {'table_name': auto_table,
                                         'except_columns': []}
                            }
