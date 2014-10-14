from __future__ import unicode_literals

from django.conf import settings as user_settings
from django.core.exceptions import ImproperlyConfigured

from django.utils import importlib
from django.utils.functional import LazyObject
from django.utils.translation import get_language_info

import pytz


def load_path_attr(path):
    i = path.rfind(".")
    module, attr = path[:i], path[i + 1:]
    try:
        mod = importlib.import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured("Error importing {0}: '{1}'".format(module, e))
    try:
        attr = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured("Module '{0}' does not define a '{1}'".format(module, attr))
    return attr


class Settings(object):
    pass


class DefaultSettings():
    ACCOUNT_OPEN_SIGNUP = True
    ACCOUNT_LOGIN_URL = "account_login"
    ACCOUNT_SIGNUP_REDIRECT_URL = "/"
    ACCOUNT_LOGIN_REDIRECT_URL = "/"
    ACCOUNT_LOGOUT_REDIRECT_URL = "/"
    ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL = "account_password"
    ACCOUNT_PASSWORD_RESET_REDIRECT_URL = "account_login"
    ACCOUNT_REMEMBER_ME_EXPIRY = 60 * 60 * 24 * 365 * 10
    ACCOUNT_USER_DISPLAY = lambda user: user.username
    ACCOUNT_CREATE_ON_SAVE = True
    ACCOUNT_EMAIL_UNIQUE = True
    ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = False
    ACCOUNT_EMAIL_CONFIRMATION_EMAIL = True
    ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
    ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "account_login"
    ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = None
    ACCOUNT_EMAIL_CONFIRMATION_URL = "account_confirm_email"
    ACCOUNT_SETTINGS_REDIRECT_URL = "account_settings"
    ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE = True
    ACCOUNT_DELETION_MARK_CALLBACK = "account.callbacks.account_delete_mark"
    ACCOUNT_DELETION_EXPUNGE_CALLBACK = "account.callbacks.account_delete_expunge"
    ACCOUNT_DELETION_EXPUNGE_HOURS = 48
    ACCOUNT_HOOKSET = "account.hooks.AccountDefaultHookSet"
    ACCOUNT_TIMEZONES = list(zip(pytz.all_timezones, pytz.all_timezones))
    ACCOUNT_LANGUAGES = [
        (code, get_language_info(code).get("name_local"))
        for code, lang in user_settings.LANGUAGES
    ]
    ACCOUNT_USE_AUTH_AUTHENTICATE = False


class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings()
        defaults = DefaultSettings()
        for obj in (defaults, user_settings):
            for attr in dir(obj):
                if attr == attr.upper():
                    val = getattr(obj, attr)
                    if (attr == 'ACCOUNT_DELETION_MARK_CALLBACK'):
                        val = load_path_attr(val)
                    if (attr == 'ACCOUNT_DELETION_EXPUNGE_CALLBACK'):
                        val = load_path_attr(val)
                    if (attr == 'ACCOUNT_HOOKSET'):
                        val = load_path_attr(val)()
                    setattr(self, attr, val)


settings = LazySettings()
