"""
Custom middleware.
"""

from django.contrib.auth import logout


class ActiveUserMiddleware(object):
    """
    Logs out a user if they've been made inactive. Ignores users that are not
    logged in.
    """
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        if not request.user.is_active:
            logout(request)
