from django.http import HttpResponse


def unnamed_untranslated_exampleview(request, *args, **kwargs):
    return HttpResponse('unnamed untranslated')


def unnamed_translated_exampleview(request, *args, **kwargs):
    return HttpResponse('unnamed translated')


def named_untranslated_exampleview(request, *args, **kwargs):
    return HttpResponse('named untranslated')


def named_translated_exampleview(request, *args, **kwargs):
    return HttpResponse('named translated')
