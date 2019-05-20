from django.http import (
    HttpResponse, HttpResponseRedirect
)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.views.generic import FormView, TemplateView
from django.contrib import messages
from users.forms import (
    LoginForm, RegisterForm,
    ProfileForm, AvatarUploadForm
)
from .models import User
from .helpers import (
    authenticate_user, register_user,
    direct_login, check_unique_email,
    generate_password_reset_token, verify_password_token
)
from stocks.helpers import get_distinct
from subscriptions.models import (
    Subscription, StockSubscription
)
from users.models import UserProfile
from stocks.models import Stock
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView
from mainsite.custom_decorators import (
    anonymous_required,
    user_login_required
)
from users.helpers import create_profile
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from favourites.models import Favourite

import configparser
import os
from django.utils.timezone import localdate
from datetime import datetime

config = configparser.ConfigParser()
config.read(os.path.join(settings.BASE_DIR, 'config.txt'))


# @method_decorator(user_login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = "mainsite/index.html"

    #
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        HIGHEST_ACCURACY_VALUE = float(config['HOMEPAGE']['HIGHEST_ACCURACY_VALUE'])
        HIGHEST_ACCURACY_COUNT = int(config['HOMEPAGE']['HIGHEST_ACCURACY_COUNT'])
        RECENT_SUBSCRIPTION_COUNT = int(config['HOMEPAGE']['RECENT_SUBSCRIPTION_COUNT'])
        if self.request.user.is_authenticated:
            if Subscription.objects.filter(user=self.request.user).exists():
                context['subscriptions'] = Stock.objects.filter(subscription__user=self.request.user,
                                                                subscription__status=True,
                                                                subscription__subscription_ends__gt=datetime.now(),
                                                                stocksubscription__valid_until__gte=datetime.now(),
                                                                status=True, stocksubscription__removed=False,
                                                                stocksubscription__status=True).distinct('symbol').all()
            else:
                context['subscriptions'] = []

            if context['subscriptions']:
                context['favorites'] = Stock.objects.filter(favourite__user=self.request.user, favourite__status=True,
                                                            status=True).exclude(
                    id__in=context['subscriptions'].values_list('id', flat=True)).distinct('symbol').all()

                qs_stocks_with_subscription = Stock.objects.filter(stocksubscription__valid_until__gte=datetime.now(),
                                                                   status=True, stocksubscription__removed=False,
                                                                   stocksubscription__status=True).exclude(
                    id__in=context['subscriptions'].values_list('id', flat=True)) \
                    .exclude(id__in=context['favorites'].values_list('id', flat=True)).distinct('symbol')

                # 2.
                newly_added_stocks = Stock.objects.filter(stocksubscription__valid_until__gte=datetime.now(),
                                                          status=True, stocksubscription__removed=False,
                                                          stocksubscription__status=True).exclude(
                    id__in=context['subscriptions'].values_list('id', flat=True)) \
                    .exclude(id__in=context['favorites'].values_list('id', flat=True)).order_by(
                    '-stocksubscription__updated_at').all()
            else:
                context['favorites'] = Stock.objects.filter(favourite__user=self.request.user, favourite__status=True,
                                                            status=True).distinct('symbol').all()
                # 1.
                qs_stocks_with_subscription = Stock.objects.filter(stocksubscription__valid_until__gte=datetime.now(),
                                                                   status=True, stocksubscription__removed=False,
                                                                   stocksubscription__status=True).exclude(
                    id__in=context['favorites'].values_list('id', flat=True)).distinct('symbol')
                # 2.
                newly_added_stocks = Stock.objects.filter(stocksubscription__valid_until__gte=datetime.now(),
                                                          status=True, stocksubscription__removed=False,
                                                          stocksubscription__status=True).exclude(
                    id__in=context['favorites'].values_list('id', flat=True)).order_by(
                    '-stocksubscription__updated_at').all()
        else:
            # 1.
            qs_stocks_with_subscription = Stock.objects.filter(stocksubscription__valid_until__gte=datetime.now(),
                                                               status=True, stocksubscription__removed=False,
                                                               stocksubscription__status=True).distinct('symbol')
            # 2.
            newly_added_stocks = Stock.objects.filter(stocksubscription__valid_until__gte=datetime.now(),
                                                      status=True, stocksubscription__removed=False,
                                                      stocksubscription__status=True).order_by(
                '-stocksubscription__updated_at').all()

        # 1. Cards of Stocks that have Subscription supported and are highly accurate
        # and not already in Subscribed list for user (top 10 as long as accuracies are
        # higher than 98% -> make the 98% value easily changeable somewhere in the code
        # also the list limits. These constants have to be easy for me to find and adjust)
        stocks_with_subscription_with_highest_accuracy = [(stock.id, stock.get_all_time_avg) for stock in
                                                          qs_stocks_with_subscription.all() if
                                                          stock.get_all_time_avg > HIGHEST_ACCURACY_VALUE]
        # sort them
        stocks_with_subscription_with_highest_accuracy = sorted(stocks_with_subscription_with_highest_accuracy,
                                                                key=lambda x: x[1])
        stocks_with_subscription_with_highest_accuracy_sorted = Stock.objects.filter(
            id__in=[i[0] for i in stocks_with_subscription_with_highest_accuracy])
        context['recommendations1'] = stocks_with_subscription_with_highest_accuracy_sorted[
                                      :HIGHEST_ACCURACY_COUNT]

        # 2. Cards of Stocks that are very newly added plans
        context['recommendations2'] = get_distinct(newly_added_stocks.exclude(
            id__in=[s.id for s in stocks_with_subscription_with_highest_accuracy_sorted]) \
                                                   .all())[:RECENT_SUBSCRIPTION_COUNT]
        return context  # dont forget to return it!

        # def get(self, request, *args, **kwargs):
        # 	# project = Project.objects.get(id=kwargs['project_id'])
        # 	return render(request, self.template_name, {'subscriptions': Subscription.objects.filter(user=self.request.user, status=True)})


def handler_400(request):
    data = {}
    return render(request, 'mainsite/errors/400.html', data)


def handler_403(request):
    data = {}
    return render(request, 'mainsite/errors/403.html', data)


def handler_404(request):
    data = {}
    return render(request, 'mainsite/errors/404.html', data)


def handler_500(request):
    data = {}
    return render(request, 'mainsite/errors/500.html', data)


def logout(request):
    auth_logout(request)
    return redirect('login')


@method_decorator(anonymous_required, name='dispatch')
class LoginFormView(FormView):
    form_class = LoginForm
    template_name = 'mainsite/login.html'
    success_url = 'index'

    def get_context_data(self, **kwargs):
        context = super(LoginFormView, self).get_context_data(**kwargs)
        context['default_form'] = "register"
        return context  # dont forget to return it!

    def authenticateUser(self, email, password):
        ##Calling the default authenticate method of Django
        return authenticate_user(self.request, email=email, password=password)

    def form_invalid(self, form):
        response = super(LoginFormView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors)
        else:
            return response

    def form_valid(self, form):
        # response = super(LoginFormView, self).form_valid(form)
        user_email = form.cleaned_data['email']
        user_password = form.cleaned_data['password']
        # remember = form.cleaned_data['remember']
        auth_success = self.authenticateUser(user_email, user_password)
        ## Authenticate user
        if self.request.is_ajax():
            if auth_success == -1:
                data = {
                    "status": 0,
                    "message": "Please validate your email to sign-in.",
                }

            # if predicted IPs/Device
            elif auth_success == "restricted":
                data = {
                    "status": 0,
                    "message": "Invalid login! Restricted IPs/Device",
                }

            #     if False
            elif not auth_success:
                data = {
                    "status": 0,
                    "message": "Invalid login!",
                }
            else:
                data = {
                    "status": 1,
                    "message": "Signing-in...",
                }
            return JsonResponse(data)
        else:
            if auth_success == -1:
                messages.add_message(self.request, messages.ERROR, 'Please verify your email to access the application')
                return redirect(self.failure_url)
            elif auth_success:
                return redirect(self.success_url)
            else:
                messages.add_message(self.request, messages.ERROR, 'Invalid login')
                return redirect(self.failure_url)


@method_decorator(anonymous_required, name='dispatch')
class RegisterFormView(FormView):
    form_class = RegisterForm
    template_name = 'mainsite/login.html'
    success_url = '/index'

    def get_context_data(self, **kwargs):
        context = super(RegisterFormView, self).get_context_data(**kwargs)
        # context['default_form'] = "register"
        return context  # dont forget to return it!

    def authenticateUser(self, email, password):
        ##Calling the default authenticate method of Django
        return authenticate_user(self.request, email=email, password=password)

    def form_invalid(self, form):
        response = super(RegisterFormView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse({
                "status": -1,
                "message": form.errors,
            })
        else:
            return response
            # if self.request.is_ajax():
            # 	return JsonResponse(form.errors, status=400)
            # else:
            # 	# return HttpResponse(form.errors)
            # 	messages.add_message(self.request, messages.ERROR, form.errors)
            # 	return super(RegisterFormView, self).form_invalid(form)
            # 	return redirect('login')

    def form_valid(self, form):
        created = False
        message = "Successfully submitted form data"
        register_data = {
            'email': form.cleaned_data['email'],
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'password': form.cleaned_data['password']
        }

        is_unique = check_unique_email(form.cleaned_data['email'])

        if not is_unique:
            message = "Please use a different email address for registration"
        else:
            created = register_user(register_data, self.request)
            message = 'Hey! Thanks for joing us :). We just sent you an email with the activation code, it will expire in 24 hours, so better click it soon!'

        if self.request.is_ajax():
            if created:
                data = {
                    "message": message,
                    "status": 1
                }
            else:
                data = {
                    "message": message,
                    "status": 0
                }
            return JsonResponse(data)
        else:
            if not is_unique:
                messages.add_message(self.request, messages.ERROR, message)
                return redirect('login')

            if settings.C_USER_EMAIL_VERIFICATION_STATUS:
                messages.add_message(self.request, messages.SUCCESS, message)
                return redirect('login')

            user_email = form.cleaned_data['email']
            user_password = form.cleaned_data['password']
            auth_success = self.authenticateUser(user_email, user_password)
            ## Authenticate user
            if created:
                return redirect('index')
            messages.add_message(self.request, messages.ERROR, message)
            return redirect('login')


def registration_awaiting_confirmation(request):
    return render(request, 'accounts.register.awaiting_confirmation')


def verify_email_registration(request, token):
    user = verify_token(token)
    if user and not user.is_email_verification_token_expired():
        data = create_profile(user.id)
        direct_login(request, user)
        return redirect('index')
    return HttpResponse('Invalid/Expired token')


def password_request_reset(request):
    return_data = {'status': 'error', 'message': 'Invalid request!'}
    if request.method == 'POST':
        if generate_password_reset_token(request.POST.get('email'), request):
            # return_data = {'status': 'success', 'message': 'Please check you registered email for instructions on recovering your account.' }
            msg = 'Please check your registered email for instructions on recovering your account.'
            if request.is_ajax():
                return JsonResponse({'status': 1, 'message': msg})
            messages.add_message(request, messages.SUCCESS, msg)
        else:
            # return_data = {'status': 'warning', 'message': 'Something went wrong trying to recover your account. Contact Support!' }
            msg = 'Something went wrong trying to recover your account. Make sure you enter your registered email!'
            if request.is_ajax():
                return JsonResponse({'status': 0, 'message': msg})
            messages.add_message(request, messages.ERROR, msg)
    return redirect('login')


def password_process_reset(request, token):
    if request.method == 'POST':
        user_password_obj = verify_password_token(request.POST.get('token'))
        if user_password_obj:
            ## Set password for user
            this_user = User.objects.get(id=user_password_obj.user_id)
            if not this_user:
                return False
            if request.POST.get('password') == request.POST.get('password_confirmation') and len(
                    request.POST.get('password')) > 6:
                this_user.password = make_password(request.POST.get('password'))
                this_user.save()
                user_password_obj.token = None
                user_password_obj.save()
                ##Takeuser to login form and allllow to login
                messages.add_message(request, messages.SUCCESS,
                                     'Password recovered, you may login with the fresh password now!')
            else:
                messages.add_message(request, messages.ERROR, 'Password recovery failed!')
        else:
            messages.add_message(request, messages.ERROR, 'Something went wrong trying to perform password recovery!')
        return redirect('login')
    # Process request
    # Show password change form
    if verify_password_token(token):
        token = token
    else:
        token = None
    context = {'token': token}
    return render(request, "mainsite/reset-password.html", context)


def create_super_user(request):
    email = 'root@email.com'
    password = 'password123'
    try:
        user = User(password=make_password(password), is_staff=True, first_name="root", email=email)
        user = user.save()
        msg = "Django admin added. Creds= Email: " + email + " Password:" + password
    except:
        msg = "Django admin already exists."
    return HttpResponse(msg)


def verify_token(token):
    try:
        user = User.objects.get(email_verification_token=token)
    except:
        return False
    if user and not user.is_email_verification_token_expired():
        user.is_email_confirmed = True
        user.email_verification_token = None
        user.save()
        # Add profile data for the user
        created = UserProfile.objects.create(user_id=user.id)
    return user
