# coding: utf-8
from __future__ import unicode_literals, absolute_import

import os

from django.conf import settings
from django.core.management import BaseCommand, call_command

from fias.exceptions import PublisherError
from fias.publish_tools import (
    ReleasePreparer,
    Releaser,
    RepoManager,
    DownloadFIASSchemaManager,
    ArchiveFIASSchemaManager,
)


class Command(BaseCommand):
    help = (
        'Основная команда для скачивания новых схем по указанному url, '
        'либо разархивирования архива БД ФИАС, содержащего в себе схемы, '
        'генерации моделей по схемам, создания миграций, и выпуска пакета '
        'в случае наличия изменений'
    )
    usage_str = (
        'Usage: python manage.py fias_update_schema --url=<fias_xsd_schemas_url> '
        'OR python manage.py fias_update_schema --path=<path_to_archive_with_schemas>'
    )

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--url',
            action='store',
            dest='url',
            help='URL со схемой строения ФИАС',
        )
        parser.add_argument(
            '--path',
            action='store',
            dest='path',
            help=(
                'Путь до zip-файла, внутри которого находится папка Schemes с '
                'xsd-схемами для построения БД'
            ),
        )
        parser.add_argument(
            '--testmode',
            action='store_true',
            dest='test_mode',
            help=(
                'Тестовый режим - пуш будет сделан в отдельную ветку, '
                'пакет релизнется на тестовом PyPi. '
                'Для включения нужно добавить флаг --testmode'
            ),
        )

    def handle(self, *args, **options):
        url = options.get('url')
        path = options.get('path')

        try:
            if url and path or not (url or path):
                raise PublisherError('Необходимо указать или url, или path!')

            print 'Запуск обновления пакета по схемам ФИАС'

            test_mode = options.get('test_mode', False)

            repo_manager = RepoManager(test_mode)
            repo = repo_manager.repo

            print '1/8 Получение схем...'
            if url:
                fias_schema_manager = DownloadFIASSchemaManager(url, repo)

            elif path:
                fias_schema_manager = ArchiveFIASSchemaManager(path, repo)

            fias_schema_manager.process_schemas()
            if not fias_schema_manager.has_schema_changes():
                # по схемам не было изменений, прекращаем работу
                raise PublisherError('Изменения в формате ФИАС не найдены')

            print '2/8 Генерация моделей...'
            call_command(
                'fias_generate_base_models',
                dst=os.path.join(settings.PROJECT_PATH, '..', 'fias', 'base_models.py'),
            )
            
            print '3/8 Проверка моделей...'
            call_command('fias_check_models')

            print '4/8 Создание и применение миграций...'
            call_command('makemigrations', 'fias')
            call_command('migrate', 'fias')

            print '5/8 Добавление новых файлов в репозиторий...'
            repo_manager.index_add()

            print '6/8 Обновление версии и лога изменений...'
            preparer = ReleasePreparer()
            preparer.prepare()
            new_version = preparer.new_version_str

            print '7/8 Обновление репозитория...'
            repo_manager.save_changes(new_version)

            print '8/8 Релиз нового пакета...'
            Releaser(new_version, test_mode).release()

            print 'Обновление пакета по новым схемам ФИАС выполнено успешно'

        except PublisherError as e:
            print str(e)
