from ftw.mobile import IS_PLONE_5_OR_GREATER
from plone import api
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


def configure_languages(default_language, supported_languages=None):
    """
    Please note that configuring supported languages is additive (if you
    call this function multiple times with different supported languages
    each time).
    """
    if not supported_languages:
        supported_languages = [default_language]

    language_tool = api.portal.get_tool('portal_languages')
    for lang in supported_languages:
        language_tool.addSupportedLanguage(lang)

    if IS_PLONE_5_OR_GREATER:
        from Products.CMFPlone.interfaces import ILanguageSchema
        registry = getUtility(IRegistry)
        language_settings = registry.forInterface(ILanguageSchema, prefix='plone')

        language_settings.available_languages = supported_languages
        language_settings.use_combined_language_codes = False
    else:
        language_tool.manage_setLanguageSettings(
            defaultLanguage=default_language,
            supportedLanguages=supported_languages,
            setUseCombinedLanguageCodes=False
        )

    language_tool.setDefaultLanguage(default_language)

    transaction.commit()


def setup_multilingual_site():
    pam_setup_tool = SetupMultilingualSite()
    pam_setup_tool.setupSite(
        api.portal.get()
    )
    transaction.commit()
