import logging

import requests
from .models import User

logger = logging.getLogger(__name__)
logger.debug('Logger in auth/logic.py loaded')


class AuthFailedError(Exception):
    def __init__(self, *args):
        self.message = ' '.join([str(arg) for arg in args])

    def __str__(self):
        return self.message


def get_portal_cookie(login, password):
    logger.debug(f"Updating cookie of user with login {login}")
    url = "https://login.school.mosreg.ru/"
    data = {
        'login': login,
        'password': password
    }
    auth_processor = requests.Session()
    try:
        portal_response = auth_processor.post(url, data=data)
    except Exception as error:
        logger.warning(f'Portal unrespond with error {error}')
        return 0, ''
    if 'DnevnikLoadTestAuth_a' in auth_processor.cookies:
        logger.debug(f"Updating cookie of user with login {login} successful")
        in_cookie = auth_processor.cookies.get('DnevnikLoadTestAuth_a')
        return 200, in_cookie
    else:
        logger.warning(f'{login} cookie updating error')
        return portal_response.status_code, ''


def register_new_user(login, password):
    logger.debug(f"User with login {login} register request")
    code, portal_cookie = get_portal_cookie(login, password)
    if code != 200 or portal_cookie == '':
        logger.debug(f"User with login {login} register fault")
        if code == 200:
            return 0, None
        return code, None
    else:
        user = User(login=login, password=password, dairy_cookie=portal_cookie)
        user.update_secret()
        user.save()
        logger.debug(f"User with login {login} register successful")
        return 200, user


def authenticate_user(login, password):
    logger.debug(f"Auth request by {login} with {len(password)*'*'}")
    try:
        user = User.objects.get(login=login, password=password)
        logger.debug(f"{login} authenticated inbase")
        return 304, user.connector
    except User.DoesNotExist:
        logger.debug(f"{login} is new user")
        code, user = register_new_user(login, password)
        if code != 200:
            logger.debug(f"{login} authenticated fault")
            return code, ''
        else:
            logger.debug(f"{login} authenticated success")
            return 200, user.connector


def reauth(user):
    logger.debug(f'{user.login} reauth request')
    code, portal_cookie = get_portal_cookie(user.login,
                                            user.password)
    if code != 200:
        logger.warning(f'{user.login} reauth fault')
        return False
    else:
        logger.debug(f'{user.login} reauthed successful')
        user.dairy_cookie = portal_cookie
        user.save()
        return True


logger.debug('File auth/logic.py loaded')
