from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def owner_required(view_func):
    """Allow only authenticated users whose role is 'owner'."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_owner:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped
