import logging
from functools import wraps
from .views import redirect_to_login


logger = logging.getLogger(__name__)
logger.debug('Logger in auth/decorators.py loaded')


def login_required(function=None, login_url=None):
    def test():
        def decorator(view_func):
            @wraps(view_func)
            def _wrapped_view(request, *args, **kwargs):
                logger.debug('Page with login required requested')
                if request.authorised:  # if authed
                    return view_func(request, *args, **kwargs)
                else:  # if no
                    return redirect_to_login(request)
            return _wrapped_view
        return decorator
    return test()(function)


logger.debug('File auth/decorators.py loaded')
