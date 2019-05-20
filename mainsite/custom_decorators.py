from django.shortcuts import redirect
from django.conf import settings
from django.http import (
    HttpResponse, HttpResponseRedirect
)

"""
 Custom Decorators
"""


# def anonymous_required(redirect_url=settings.ANONYMOUS_REDIRECT_URL):
#     """
#     Decorator for views that allow only unauthenticated users to access view.
#     Usage:
#     @anonymous_required(redirect_url='company_info')
#     def homepage(request):
#         return render(request, 'homepage.html')
#     """
#     def _wrapped(view_func, *args, **kwargs):
#         def check_anonymous(request, *args, **kwargs):
#          and   view = view_func(request, *args, **kwargs)
#             if request.user.is_authenticated():
#                 return redirect(redirect_url)
#             return view
#         return check_anonymous
#     return _wrapped

def user_login_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated or request.user.is_admin():
            return redirect(settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func


def admin_login_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated or not request.user.is_admin():
            return redirect(settings.ADMIN_LOGIN_URL)
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func


def anonymous_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user and request.user.is_authenticated and not request.user.is_admin():
            return redirect(settings.ANONYMOUS_REDIRECT_URL)
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func


def admin_anonymous_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user and request.user.is_authenticated and request.user.is_admin():
            return redirect(settings.ADMIN_ANONYMOUS_REDIRECT_URL)
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func
