import json
from django.http import (
    HttpResponse, HttpResponseRedirect
)
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from .models import User, UserProfile
from django.contrib.auth.decorators import login_required
from mainsite.custom_decorators import anonymous_required
# from django.views.generic import FormView
from django.core import serializers
from django.views.generic import FormView, TemplateView
from .forms import (
    LoginForm, RegisterForm,
    ProfileForm, AvatarUploadForm, RestrictedIPDeviceForm
)
from mainsite.models import LoginLog, RestrictedIPDevice
from mainsite.helpers import get_location_info_from_ip
import random, string
from django.contrib import messages
from cities_light.models import Country, Region, City

# def index(request):
# 	context = {}
# 	return render(request, 'users/index.html', context)

"""
****** Profile methods start
"""


@method_decorator(login_required, name='dispatch')
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/index.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['user_profile'] = self.request.user.userprofile
        context['guess_geo'] = False
        context['countries'] = Country.objects.all()
        if not self.request.user.userprofile.country:
            context['guess_geo'] = True
            context['geo'] = get_location_info_from_ip(self.request)
            if context['geo']['geoplugin_countryCode']:
                guessed_country_id = Country.objects.get(code2=context['geo']['geoplugin_countryCode'])
                context['states'] = Region.objects.filter(country_id=guessed_country_id)
            else:
                context['states'] = Region.objects.all()
            context['form'] = AvatarUploadForm()
        else:
            context['states'] = Region.objects.filter(country_id=self.request.user.userprofile.country)
            context['cities'] = City.objects.filter(region_id=self.request.user.userprofile.state)
            context['form'] = AvatarUploadForm()
        return context


def edit_restricted_ip_device(request):
    if request.method == 'POST':
        user = request.user
        id = request.POST.get('id')
        ip_device = request.POST.get('ip_device')
        result = RestrictedIPDevice.objects.get(user=user, id=id)
        result.ip_device = ip_device
        result.save()
        return HttpResponseRedirect(reverse('account-settings'))


def remove_restricted_ip_device(request):
    if request.method == 'GET':
        if request.GET.get('id'):
            if RestrictedIPDevice.objects.get(id=request.GET.get('id')).who_did == "user":
                RestrictedIPDevice.objects.filter(id=request.GET.get('id')).delete()
                return redirect('account-settings')
    return HttpResponse('Invalid request')


def add_restricted_ip_device(request):
    if request.method == 'POST':
        user = request.user
        ip_device = request.POST.get('ip_device')
        if not RestrictedIPDevice.objects.filter(ip_device=ip_device).exists():
            RestrictedIPDevice.objects.create(user=user, ip_device=ip_device, who_did="user")
        return HttpResponseRedirect(reverse('account-settings'))


def save_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        userprofile, created = UserProfile.objects.get_or_create(user_id=user.id)
        userprofile.phone = request.POST.get('phone')
        userprofile.country = request.POST.get('country')
        userprofile.state = request.POST.get('state')
        userprofile.city = request.POST.get('city')
        userprofile.save()
        user.save()
        messages.add_message(request, messages.SUCCESS, 'Profile updated!')
        return redirect("profile")
    messages.add_message(request, messages.ERROR, 'Invalid request')
    return HttpResponseRedirect(reverse('profile'))


class AccountSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/account-settings.html'

    def get_context_data(self, **kwargs):
        context = super(AccountSettingsView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['login_logs'] = LoginLog.objects.filter(user=self.request.user.get_email())
        restricted_ips = RestrictedIPDevice.objects.filter(user=self.request.user).order_by("-id")
        result = []
        idx = 1
        for ip in restricted_ips:
            ele = {
                "id": idx,
                "pk": ip.id,
                "ip_device": ip.ip_device,
                "blocked_by_admin": ip.blocked_by_admin,
                "who_did": ip.who_did,
            }
            result.append(ele)
            idx += 1
        context['restricted_ips'] = json.dumps(result)
        context['restricted_tab'] = False
        context['form'] = AvatarUploadForm()
        return context


"""
****** Profile methods end ******
"""


class SummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'summary/index.html'

    def get_context_data(self, **kwargs):
        context = super(SummaryView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class StockView(LoginRequiredMixin, TemplateView):
    template_name = 'stocks/single.html'

    def get_context_data(self, **kwargs):
        context = super(StockView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ActivityView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/activity.html'

    def get_context_data(self, **kwargs):
        context = super(ActivityView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


def upload_avatar(request):
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    form = AvatarUploadForm(request.POST, request.FILES, instance=user_profile)
    data = {'status': False}
    if form.is_valid():
        user_profile = form.save()
        data = {'status': True, 'name': user_profile.avatar.name, 'url': user_profile.avatar.url}
    # return JsonResponse({'user': request.user.id})
    return redirect('profile')


def remove_avatar(request):
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    user_profile.avatar = ''
    user_profile.save()
    return redirect('profile')


def api_country(request):
    if request.get('country_code'):
        context['countries'] = Country.objects.filter(code2, request.get('country_code')).first()
    else:
        context['countries'] = Country.objects.all()
    return JsonResponse(context)


def api_state(request, code):
    context = {}
    if code:
        context['states'] = serializers.serialize('json', Region.objects.filter(country_id=code))  # ()
    else:
        context['states'] = serializers.serialize('json', Region.objects.all())
    return JsonResponse(context)


def api_city(request, code):
    context = {}
    if code:
        context['cities'] = serializers.serialize('json', City.objects.filter(region_id=code))
    else:
        context['cities'] = serializers.serialize('json', City.objects.all())
    return JsonResponse(context)


# Testing, will  be removed later
# @anonymous_required
def test(request):
    context = {}
    # user_profile = UserProfile.objects.filter(user=request.user.id)
    # return HttpResponse(request.user.userprofile)
    return JsonResponse(get_location_info_from_ip(request))
