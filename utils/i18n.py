"""
Internationalization and localization utilities.

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

from pyi18n import PyI18n
from pyi18n.loaders import PyI18nYamlLoader

__all__ = ["I18n"]


class I18n:
    """
    Internationalization and localization class.
    Provides a simple interface to get translated strings.
    """

    locales = {"en-US", "zh-TW", "zh-CN"}
    i18n_instance = PyI18n(tuple(locales), loader=PyI18nYamlLoader("locales", namespaced=True))
    i18n_get = i18n_instance.gettext

    @classmethod
    def get(cls, key: str, language: str, **kwargs) -> str:
        """
        Get a translated string.

        :param key: The key of the string.
        :type key: str
        :param language: The language to get the string in.
        :type language: str
        :param kwargs: The arguments to format the string with.
        :type kwargs: dict

        :return: The translated string.
        :rtype: str
        """
        if language not in cls.locales:
            language = "en-US"
        return cls.i18n_get(language, key, **kwargs)
