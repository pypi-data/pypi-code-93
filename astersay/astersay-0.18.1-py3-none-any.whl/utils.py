#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
import json
import re
from gettext import gettext as _
from hashlib import sha256
from importlib import import_module
from os import system as os_system, remove as os_remove
from os.path import join as path_join, exists, basename
from types import GeneratorType
from unidecode import unidecode
from wave import open as wave_open


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as e:
        raise ImportError(
            "%s doesn't look like a module path." % dotted_path
        ) from e

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class' % (
                module_path, class_name)
        ) from e


def to_flat_list(data, skip=None, prebool=None, sort=False):
    """
    Преобразовывает многоуровневый объект в [отсортированный] плоский список.
    """
    result = []
    if skip is None:
        skip = ()
    if prebool is None:
        prebool = int

    def collect(item, prefix=''):
        if isinstance(item, dict):
            for key, value in item.items():
                if key in skip:
                    continue
                # Recursive collection for internal values.
                collect(value, prefix='%s%s:' % (prefix, key))
        elif isinstance(item, (list, tuple, range, GeneratorType)):
            for key, value in enumerate(item):
                # Recursive collection for internal values.
                collect(value, prefix='%s%d:' % (prefix, key))
        else:
            if isinstance(item, bool):
                value = prebool(item)
            else:
                value = item
            result.append('%s%s' % (prefix, str(value)))

    collect(data)
    if sort:
        result.sort()
    return result


def to_unique_string(data, skip=None, prebool=None, separator=';'):
    """
    Преобразовывает многоуровневый объект в уникальную строку.
    """
    if data is None:
        return ''
    elif isinstance(data, str):
        return data
    flat_list = to_flat_list(data, skip=skip, prebool=prebool, sort=True)
    return separator.join(flat_list)


def make_checksum(data, *args, **kwargs):
    uniq = to_unique_string(data, *args, **kwargs)
    return sha256(uniq.encode('utf-8')).hexdigest()


def prepare_dialog_name(s):
    """
    Преобразовывает имена разных алфавитов в латинницу и удаляет/заменяет
    лишние символы.
    """
    return unidecode(s).replace(' ', '_').replace('-', '_').replace("'", "")


def levenshtein_distance(text_1, text_2):
    """Алгоритм вычисления дистанции Левенштейна между двумя текстами."""

    length_1, length_2 = len(text_1), len(text_2)
    # Первым должен быть указан наименьший текст.
    if length_1 > length_2:
        text_1, text_2 = text_2, text_1
        length_1, length_2 = length_2, length_1

    current = range(length_1 + 1)
    for i in range(1, length_2 + 1):
        previous, current = current, [i] + [0] * length_1
        for j in range(1, length_1 + 1):
            add = previous[j] + 1
            delete = current[j - 1] + 1
            change = previous[j - 1]
            if text_1[j - 1] != text_2[i - 1]:
                change += 1
            current[j] = min(add, delete, change)
    return current[length_1]


def make_voice(logger, convertor, synthesize, storage_path, make_message, text,
               early=False, **kwargs):
    """
    Функция для создания головового файла(ов) для текста по переданным
    обработчикам синтезатора.
    """
    logger_debug = logger.debug
    logger_info = logger.info
    logger_info(_('Начинается синтез речи.'))

    # Убираем лишние пробелы.
    text = re.sub(r'\s+', ' ', text)

    def _find_voice(checksum):
        voice = path_join(storage_path, checksum)
        filename = '%s.wav' % voice
        # Именно такой файл уже есть, не нужно синтезировать.
        if exists(filename):
            logger_info(
                _('Речь %r существует и будет взята из хранилища.'), voice)
            found = True
        else:
            found = False
        return voice, filename, found

    def _save_info(voice, spec):
        spec_filename = '%s.json' % voice
        json.dump(spec, open(spec_filename, 'w'), indent=4, ensure_ascii=False)
        logger_debug(_('Сохранён файл спецификации: %s'), spec_filename)

    def _synthesize(voice, filename, message, spec):
        _save_info(voice, spec)

        audio_data = synthesize(message)

        src_filename = '%s.%s' % (voice, convertor['src_format'])
        with open(src_filename, 'wb') as f:
            f.write(audio_data)
        logger_info(_('Записан исходный файл речи: %s'), src_filename)
        command = convertor['command'] % (src_filename, filename)
        os_system(command)
        logger_info(_('Записан конечный файл речи: %s'), filename)

        if convertor.get('src_delete'):
            os_remove(src_filename)
        return True

    # Символ | является разделителем на несколько составных файлов, но
    # он может быть и цельным.
    message = make_message(text.replace('|', ''))
    spec = message.copy()
    spec['convertor'] = convertor
    checksum = make_checksum(spec)
    voice, filename, found = _find_voice(checksum)

    texts = [x for x in text.split('|') if x.strip()]
    if len(texts) == 1:
        if not found:
            logger_info(_('Синтезирую в речь текст: %r'), text)
            _synthesize(voice, filename, message, spec)
    elif not found:
        chunks = []
        for chunk_text in texts:
            chunk_message = make_message(chunk_text)
            chunk_spec = chunk_message.copy()
            chunk_spec['convertor'] = convertor
            chunk_checksum = make_checksum(chunk_spec)
            chunk_voice, chunk_filename, found = _find_voice(chunk_checksum)
            if not found:
                logger_info(_('Синтезирую в речь текст: %r'), chunk_text)
                _synthesize(chunk_voice, chunk_filename, chunk_message,
                            chunk_spec)
            chunks.append((chunk_voice, chunk_filename))

        # Если это заблаговременный синтез частей текста, то не собираем
        # конечный файл, а только все части.
        if early:
            logger_debug(_('Для предварительного синтеза речи конечный '
                           'файл не собирается.'))
            return voice

        frames = []
        params = None
        last_voice = chunks[-1][0]
        for chunk_voice, chunk_filename in chunks:
            with wave_open(chunk_filename) as f:
                if chunk_voice == last_voice:
                    params = f.getparams()
                frames.append(f.readframes(f.getnframes()))
        # Записываем информацию по слитому файлу.
        spec['chunks'] = [basename(v) for v, f in chunks]
        _save_info(voice, spec)
        # Записываем конечный, слитый файл.
        with wave_open(filename, 'wb') as f:
            f.setparams(params)
            for frame in frames:
                f.writeframes(frame)

    return voice
