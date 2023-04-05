"""
Internationalization and localization utilities.
"""

from typing import Optional, Union

from pyi18n import PyI18n
from pyi18n.loaders import PyI18nYamlLoader


class I18n:
    """
    Internationalization and localization class.
    Provides a simple interface to get translated strings.
    """

    locales = {"en-US", "zh-TW", "zh-CN"}
    i18n_instance = PyI18n(tuple(locales), loader=PyI18nYamlLoader("locales", namespaced=True))
    i18n_get = i18n_instance.gettext

    @classmethod
    def get(cls, key: str, language: str, args: Optional[Union[list, tuple]] = None) -> str:
        """
        Get a translated string.

        :param key: The key of the string.
        :type key: str
        :param language: The language to get the string in.
        :type language: str
        :param args: The arguments to format the string with.
        :type args: Optional[Union[list, tuple]]
        """
        if language not in cls.locales:
            language = "en-US"
        out = cls.i18n_get(language, key)
        if args:
            if not isinstance(args, (list, tuple)):
                raise TypeError(f"Expected list or tuple, got {type(args).__name__}.")
            if len(args) != out.count("%arg%"):
                raise ValueError(
                    f"Number of arguments does not match number of placeholders in string '{out}'."
                )
            for arg in args:
                out = out.replace("%arg%", str(arg), 1)
        return out
