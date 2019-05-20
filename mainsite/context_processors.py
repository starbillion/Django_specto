from django.conf import settings  # import the settings file
from users.helpers import get_user_avatar as get_avatar
from subscriptions.models import Subscription


def active_theme(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    # Ignore, will use later, not required for theme
    return {'MY_ACTIVE_THEME': 'metronic'}


def get_user_avatar(request):
    try:
        user = request.user
    except:
        user = None
    return {'CP_USER_AVATAR': get_avatar(user)}
