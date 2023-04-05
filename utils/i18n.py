"""
Internationalization and localization utilities.
"""

from pyi18n import PyI18n
from pyi18n.loaders import PyI18nYamlLoader


class I18n:
    """
    Internationalization and localization class.
    Provides a simple interface to get translated strings.
    """

    locales = {"en-US", "zh-TW", "zh-CN"}
    i18n_loader = PyI18nYamlLoader("locales", namespaced=True)
    i18n_instance = PyI18n(tuple(locales), loader=i18n_loader)
    i18n_get = i18n_instance.gettext

    @classmethod
    def get(cls, key: str, language: str = "en-US") -> str:
        """
        Get a translated string.

        :param key: The key of the string.
        :type key: str
        :param language: The language to get the string in.
        :type language: str
        """
        if language not in cls.locales:
            language = "en-US"
        return cls.i18n_get(language, key)
