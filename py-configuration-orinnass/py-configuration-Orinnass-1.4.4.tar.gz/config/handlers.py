# from pymysql import Connection as pymySQLConnection
# from logging import Handler, LogRecord
#
#
# class DBHandler(Handler):
#     """
#     Обработчик логирования в БД
#     """
#     # TODO: Дописать обработчик
#     def __init__(self, connection: pymySQLConnection, table: str):
#         super().__init__()
#         self.__connection = connection
#         self.__cursor = connection.cursor()
#         self.__table = table
#
#     def emit(self, record: LogRecord) -> None:
#         self.__cursor.execute(f"insert into `{self.__table}` (`logger`, `level_log`, `message`, `time`) "
#                               f"values (%s, %s, %s, %s)", [record.name, record.levelname, record.message, record.asctime])
#         self.__connection.commit()
