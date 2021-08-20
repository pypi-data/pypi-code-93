import logging
import os

from django.db import transaction
from django.db.models import Q

from isc_common.common import blinkString, green, red, blue
from isc_common.datetime import StrToDate
from isc_common.fields.name_field import NameField
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class Import_command_stucturesQuerySet(AuditQuerySet):
    pass


class Import_command_stucturesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'path': record.path,
            'lastmodified': record.lastmodified,
        }
        return res

    def get_queryset(self):
        return Import_command_stucturesQuerySet(self.model, using=self._db)


class Import_command_stuctures(AuditModel):
    path = NameField()
    objects = Import_command_stucturesManager()

    @classmethod
    def import_add_info(cls, filename):
        import openpyxl
        from lfl_admin.statistic.models.import_command_stuctures_log import Import_command_stuctures_log
        from isc_common.auth.models.user import User
        from lfl_admin.competitions.models.clubs import Clubs
        from lfl_admin.competitions.models.calendar import Calendar
        from lfl_admin.competitions.models.command_structure_view import Command_structure_view
        from lfl_admin.competitions.models.players import Players

        if os.path.exists(filename):
            with transaction.atomic():
                _, _filename = os.path.split(filename)
                import_command_stuctures = cls.objects.create(path=_filename)

                wb = openpyxl.load_workbook(filename)
                idx = wb.sheetnames.index('1. Составы')
                wb.active = idx
                sheet = wb.active
                cnt_error = 0
                for i in range(2, 1000000):
                    Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=blinkString(text=f'Строка #{i}', blink=False, bold=True))

                    match_date_time = StrToDate(sheet[f'A{i}'].value)
                    print(f'#{i} match_date_time: {match_date_time}')
                    Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=f'Дата: {match_date_time}')

                    if match_date_time is None:
                        cnt_error += 1
                    else:
                        cnt_error = 0

                    if cnt_error == 5:
                        break

                    fio = sheet[f'B{i}'].value
                    Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=f'fio: {fio}')
                    if fio is None or fio in ['Сумма полевых']:
                        continue

                    try:
                        last_name, first_name = fio.strip().split(' ')
                    except Exception as ex:
                        print(fio)
                        raise ex

                    user_query = User.objects.filter(last_name=last_name, first_name=first_name)
                    cnt = user_query.count()

                    if cnt == 0:
                        Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=blinkString(text=f'Игрок : {fio} не найден', blink=False, bold=True))
                        continue

                    user = user_query[0]

                    Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=blinkString(text=f'Игрок : {str(user)} найден', blink=False, color=green, bold=True))

                    club = sheet[f'E{i}'].value
                    Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=f'club: {club}')
                    if club in ['Вратарь', 'Сумма вратари']:
                        continue

                    club_query = Clubs.objects.filter(name__contains=club)
                    cnt = club_query.count()
                    if cnt == 0:
                        Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=blinkString(text=f'Комманда : {club} не найдена', blink=False, color=red, bold=True))
                        continue

                    club = club_query[0]
                    Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=blinkString(text=f'Комманда : {str(club)} найдена', blink=False, color=green, bold=True))

                    num = sheet[f'F{i}'].value
                    Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=f'num: {num}')
                    if num is None:
                        continue

                    calendar_query = Calendar.objects.filter(match_date_time=match_date_time)
                    calendar_query = calendar_query.filter(Q(away=club) | Q(home=club))

                    cnt = calendar_query.count()
                    if cnt == 0:
                        Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=blinkString(text=f'{match_date_time} Не найдены матчи для кооманды {str(club)}', blink=False, color=red, bold=True))
                    else:
                        Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=blinkString(text=f'{match_date_time} Найдено : {cnt} матчей для кооманды {str(club)}', blink=False, color=green, bold=True))

                    for match in calendar_query:
                        command_structure_query = Command_structure_view.objects.filter(match=match, num__contains=num)
                        cnt = command_structure_query.count()

                        if cnt == 0:
                            Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=blinkString(text=f'Для матча : {str(match)} игрок с № {num} не найден', blink=False, color=red, bold=True))
                            continue

                        for command_structure in command_structure_query:
                            new_player = Players.objects.get(person__user=user)
                            Import_command_stuctures_log.objects.create(imports=import_command_stuctures, log=blinkString(text=f'Для матча : {str(match)} замена player: {command_structure.player} на player {new_player}', color=blue, bold=True))
                            command_structure.player_histories.player = new_player
                            command_structure.player_histories.save()


        else:
            raise Exception(f'file: {filename} not exists')

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Разные картинки '
