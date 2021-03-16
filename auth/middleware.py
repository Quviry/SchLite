import datetime
import logging

from django.utils.deprecation import MiddlewareMixin
from .models import User, Visits

logger = logging.getLogger(__name__)
logger.debug('Logger in auth/middleware.py loaded')


class AuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        logger.debug('AuthMiddleware inited')

    def __call__(self, request):
        # before view
        request.authorised = False
        request.Student = None
        auth_cookie = request.COOKIES.get('auth_dat', '')
        try:
            user = User.objects.get(connector=auth_cookie)
            request.User = user
            request.authorised = True
            new_visit = Visits.objects.create(ip=request.META['REMOTE_ADDR'], requested=request.path, user=user)
            logger.debug(f'{user.login} request logged')
        except User.DoesNotExist:
            request.User = None
            new_visit = Visits.objects.create(ip=request.META['REMOTE_ADDR'], requested=request.path, user=None)
            logger.debug(f'Anonymous user request logged')
        new_visit.save()
        # run view
        response = self.get_response(request)
        # response_code after
        return response


logger.debug('File auth/middleware.py loaded')
