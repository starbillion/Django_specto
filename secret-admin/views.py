from django.http import (
    HttpResponse, HttpResponseRedirect
)
from mainsite.models import RestrictedIPDevice
from django.urls import reverse
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
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timedelta
from subscriptions.models import StockSubscription, Subscription
from mainsite.models import User
from mainsite.helpers import (
    authenticate_user, register_user,
    direct_login, check_unique_email,
    generate_password_reset_token, verify_password_token
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView
from mainsite.custom_decorators import (
    admin_anonymous_required,
    admin_login_required
)
from users.helpers import create_profile
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.core import serializers

from stocks.models import (
    Stock, StockPrediction,
)
import json
from django.utils.timezone import localdate
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site


@method_decorator(admin_login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = "admin/pages/index.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        # context['stocks'] =  serializers.serialize("json", Stock.objects.prefetch_related('stocksubscription_set').all().order_by('id'))
        context['stocks'] = serializers.serialize("json", Stock.objects.all().order_by('id'))
        return context  # dont forget to return it!


@method_decorator(admin_login_required, name='dispatch')
class ManageRestrictedIPsDeviceView(TemplateView):
    template_name = "admin/pages/manage_restricted_ips_device.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        # remaining days of subscription is less than 10
        result = []
        users = User.objects.filter(is_active=True, is_staff=False)
        idx = 1
        for user in users:
            # end
            ele = {
                "id": idx,
                "pk": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": datetime.strftime(user.created_at, '%Y-%m-%d %H:%M:%S')
            }
            idx += 1
            result.append(ele)
        context['users'] = json.dumps(result)
        return context  # dont forget to return it!


@method_decorator(admin_login_required, name='dispatch')
class ManageSubscriptionsUsersView(TemplateView):
    template_name = "admin/pages/manage_subs_of_users.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        # remaining days of subscription is less than 10
        result = []
        expire_subs = Subscription.objects.filter(status=True,
                                                  subscription_ends__lte=datetime.now() + timedelta(
                                                      days=settings.EXPIRED_DAY))
        idx = 1
        for item in expire_subs:
            stock = Stock.objects.get(id=item.stock_id)
            user = User.objects.get(id=item.user_id)
            # begin calculating the remaining days
            today = datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            end_date = datetime.strptime(datetime.strftime(item.subscription_ends, '%Y-%m-%d %H:%M:%S'),
                                         '%Y-%m-%d %H:%M:%S')
            delta = end_date - today
            remaining_days = delta.days

            # end
            ele = {
                "id": idx,
                "user_id": user.id,
                "email": user.email,
                "symbol": stock.symbol,
                "name": stock.name,
                "date_end": datetime.strftime(item.subscription_ends, '%Y-%m-%d %H:%M:%S'),
                "remaining_days": remaining_days,
            }
            idx += 1
            result.append(ele)
        context['subs'] = json.dumps(result)
        return context  # dont forget to return it!


@method_decorator(admin_login_required, name='dispatch')
class ManageSubscriptionsView(TemplateView):
    template_name = "admin/pages/manage_subscriptions.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['stocks'] = serializers.serialize("json", Stock.objects.all().order_by('id'))
        return context  # dont forget to return it!


# @method_decorator(admin_login_required, name='dispatch')
def send_email_to_expired_user(request):
    user_id = request.POST.get('user_id')
    user = User.objects.get(id=user_id)
    symbol = request.POST.get('symbol')
    access_site = get_current_site(request)
    rendered_email_body = render_to_string('emails/subs_expire_send.html',
                                           {'symbol': symbol, 'domain': access_site.domain})
    created = send_mail(settings.C_SUBS_EXPIRE_SUBJECT, rendered_email_body, settings.C_EMAIL_VERIFICATION_SENDER,
                        [user.email])
    if created:
        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False})


# @method_decorator(admin_login_required, name='dispatch')
def update_stock_plan_subscriptions(request):
    data = {'status': [], 'data': []}
    plan_durations = request.POST.getlist('plan_duration[]')
    prices = request.POST.getlist('price[]')
    statuses = request.POST.getlist('status[]')
    valid_untils = request.POST.getlist('valid_until[]')
    ids = request.POST.getlist('ids[]')
    # max_months_purchasables = request.POST.getlist('max_months_purchasable[]')
    max_months_purchasables = request.POST.get('max_months_purchasable')

    # if not all(plan_durations) or not all(prices) or not all(valid_untils) or not all(max_months_purchasables):
    if not all(plan_durations) or not all(prices) or not all(valid_untils):
        return JsonResponse({'data': 'error'}, status=405)

    stock = request.POST.get('stock')
    stock_obj = Stock.objects.get(symbol=stock)
    for i in range(0, len(plan_durations)):
        ## Find if the plan already exists for the user
        duration = plan_durations[i]
        status = statuses[i]
        price = prices[i]
        valid_until = valid_untils[i]
        # max_months_purchasable = max_months_purchasables
        # subs, created = StockSubscription.objects.update_or_create(plan_duration=duration, stock_id=stock_obj.pk,
        #                                                            removed=False, valid_until=valid_until, max_months_purchasable=max_months_purchasables,
        #                                                            defaults={"status": status, "price": price})
        if ids[i]:
            temp = StockSubscription.objects.get(id=ids[i], stock_id=stock_obj.pk)
            temp.plan_duration = duration
            temp.removed = False
            temp.valid_until = valid_until
            temp.max_months_purchasable = max_months_purchasables
            temp.price = price
            temp.status = status
            temp.save()
        else:
            temp = StockSubscription(stock_id=stock_obj.pk,
                                     plan_duration=duration,
                                     removed=False,
                                     valid_until=valid_until,
                                     max_months_purchasable=max_months_purchasables,
                                     price=price,
                                     status=status)
            temp.save()
        # data['status'].append(created)
        data['status'] = True
    return JsonResponse({'data': data})


# @method_decorator(admin_login_required, name='dispatch')
def remove_stock_subscriptions(request):
    data = {}
    plan_id = request.POST.get('plan_id')
    status = StockSubscription.objects.filter(id=plan_id).update(removed=True)
    data['status'] = status
    return JsonResponse({'data': data})


@method_decorator(admin_anonymous_required, name='dispatch')
class LoginFormView(FormView):
    form_class = LoginForm
    template_name = 'admin/pages/login.html'
    success_url = 'admin.index'
    failure_url = 'admin.login'

    def get_context_data(self, **kwargs):
        context = super(LoginFormView, self).get_context_data(**kwargs)
        context['default_form'] = "login"
        return context  # dont forget to return it!

    def authenticateUser(self, email, password):
        ##Calling the default authenticate method of Django
        return authenticate_user(self.request, email=email, password=password, only_admin=True)

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
        auth_success = self.authenticateUser(user_email, user_password)
        ## Authenticate user
        if self.request.is_ajax():
            if auth_success == -1:
                data = {
                    "status": 0,
                    "message": "Please validate your email to sign-in.",
                }
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


# @method_decorator(admin_login_required, name='dispatch')
def get_stock_predictions_single(request):
    stock = Stock.objects.get(symbol=request.POST.get('symbol'))
    data = {}
    data['stock_predictions'] = serializers.serialize("json",
                                                      StockPrediction.objects.filter(stock_id=stock.pk).order_by('id'))
    return JsonResponse(data)


def add_single_user_ip_device(request):
    user = User.objects.get(id=int(request.POST.get('user_id')))
    ip_device = request.POST.get('ip_device')
    # if request.POST.get('blocked_status') == 'on':
    #     blocked_status = True
    # else:
    #     blocked_status = False

    if not RestrictedIPDevice.objects.filter(ip_device=ip_device).exists():
        created = RestrictedIPDevice.objects.create(user=user, ip_device=ip_device, who_did="admin")
    if created:
        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False})


def add_single_user_ip_device_from(request):
    user = User.objects.get(id=int(request.POST.get('user_id')))
    ip_device = request.POST.get('ip_device')
    # if request.POST.get('blocked_status') == 'on':
    #     blocked_status = True
    # else:
    #     blocked_status = False

    if not RestrictedIPDevice.objects.filter(ip_device=ip_device).exists():
        created = RestrictedIPDevice.objects.create(user=user, ip_device=ip_device, who_did="admin")
        return redirect('admin.single-user-restricted-ip-device', user_id=user.id)


def edit_single_user_ip_device(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        ip_device = request.POST.get('ip_device')
        # blocked_status = request.POST.get('blocked_status')
        # if blocked_status == 'on':
        #     status = True
        # else:
        #     status = False
        result = RestrictedIPDevice.objects.get(id=id)
        user = User.objects.get(email=result.user)
        # result.blocked_by_admin = status
        result.ip_device = ip_device
        result.save()
        return redirect('admin.single-user-restricted-ip-device', user_id=user.id)


def remove_restricted_ip_device(request):
    if request.method == 'GET':
        if request.GET.get('id'):
            if RestrictedIPDevice.objects.filter(id=request.GET.get('id')).exists():
                result = RestrictedIPDevice.objects.get(id=request.GET.get('id'))
                user = User.objects.get(email=result.user)
                RestrictedIPDevice.objects.filter(id=request.GET.get('id')).delete()

                return redirect('admin.single-user-restricted-ip-device', user_id=user.id)
    return HttpResponse('Invalid request')


# @method_decorator(admin_login_required, name='dispatch')
def single_user_ip_device(request, user_id):
    result = []
    user = User.objects.get(id=user_id)
    restricted_ip_devices = RestrictedIPDevice.objects.filter(user=user)
    idx = 1
    for ip_device in restricted_ip_devices:
        # end
        ele = {
            "id": idx,
            "pk": ip_device.id,
            "user_id": user.id,
            "ip_device": ip_device.ip_device,
            "created_at": datetime.strftime(ip_device.created_at, '%Y-%m-%d %H:%M:%S'),
            "updated_at": datetime.strftime(ip_device.updated_at, '%Y-%m-%d %H:%M:%S'),
            "blocked_status": ip_device.blocked_by_admin,
            "who_did": ip_device.who_did,
        }
        idx += 1
        result.append(ele)
    return render(request, 'admin/pages/sing_user_restricted_ip_device.html',
                  {'result': json.dumps(result), 'user': user})


# @method_decorator(admin_login_required, name='dispatch')
def stock_single(request, symbol):
    data = {}
    data['stock'] = Stock.objects.get(symbol=symbol)
    data['stock_predictions'] = serializers.serialize("json", StockPrediction.objects.filter(
        stock_id=data['stock'].id).order_by('id'))
    return render(request, 'admin/pages/stock_single.html', data)


# @method_decorator(admin_login_required, name='dispatch')
def upload_csv_predictions(request):
    response = []
    responseData = {'status': 0, 'message': ''}
    if request.method != 'POST':
        return JsonResponse()
    try:
        csv_file = request.FILES["file"]
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'status': 'Invalid csv format'})
        # if file is too large, return
        if csv_file.multiple_chunks():
            return JsonResponse({'message': "Uploaded file is too big (%.2f MB)." % (csv_file.size / (1000 * 1000),)})

        file_data = csv_file.read().decode("utf-8")
        lines = file_data.split("\n")
        # loop over the lines and save them in db. If error , store as string and then display
        i = 0
        for line in lines:
            # Skipping the first row, as it contains column labels
            if i == 0:
                i = 1
                continue
            fields = line.split(",")
            if len(fields) != 5:
                continue
            data_dict = {}
            data_dict["date"] = fields[0]
            data_dict["high"] = fields[1]
            data_dict["low"] = fields[2]
            data_dict["close"] = fields[3]
            data_dict["accuracy_prev_day"] = fields[4]
            response.append(data_dict)
        all_stock = serializers.serialize("json", StockPrediction.objects.filter(
            stock_id=request.POST.get('stock_id')).order_by('id'))
        return JsonResponse({'status': 'Success', 'data': response, 'all_stock': all_stock})
    except Exception as e:
        return JsonResponse({'status': 'Error', 'message': 'Error in request', 'error': str(e)})
    return JsonResponse({'status': 'Error'})


# @method_decorator(admin_login_required, name='dispatch')
def update_stock_predictions(request):
    if request.method == 'POST':
        return
        if request.POST.get('id') == '':
            return HttpResponse("Invalid request")
        else:
            StockPrediction.objects.filter(id=request.POST.get('id')).update(date=request.POST.get('date'),
                                                                             high=request.POST.get('high'),
                                                                             low=request.POST.get('low'),
                                                                             close=request.POST.get('close'),
                                                                             accuracy_prev_day=request.POST.get(
                                                                                 'accuracy_prev_day'),
                                                                             status=request.POST.get(
                                                                                 'status') == '1' and True or False)
        return redirect('admin.stock_single', kwargs={'symbol': request.POST.get('symbol')})
    # Do some fancy stuff
    return HttpResponse('Invalid request')


# @method_decorator(admin_login_required, name='dispatch')
def update_stock(request):
    if request.method == 'POST':
        if request.POST.get('id') == '':
            obj = Stock.objects.create(
                symbol=request.POST.get('symbol'),
                name=request.POST.get('name'),
                sector=request.POST.get('sector'),
                industry=request.POST.get('industry'),
                status=request.POST.get('status') == '1' and True or False,
            )
        else:
            Stock.objects.filter(id=request.POST.get('id')).update(symbol=request.POST.get('symbol'),
                                                                   name=request.POST.get('name'),
                                                                   sector=request.POST.get('sector'),
                                                                   industry=request.POST.get('industry'),
                                                                   status=request.POST.get(
                                                                       'status') == '1' and True or False)
        return HttpResponseRedirect(reverse('admin.index'))
    # Do some fancy stuff
    return HttpResponse('Invalid request')


# @method_decorator(admin_login_required, name='dispatch')
def update_stock_predictions(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'Error'})
    responseData = {'status': 'error', 'message': 'No data!'}
    if len(request.POST.getlist("data[]['date']")) > 0:
        prediction_date_set = request.POST.getlist("data[]['date']")
        high_set = request.POST.getlist("data[]['high']")
        low_set = request.POST.getlist("data[]['low']")
        close_set = request.POST.getlist("data[]['close']")
        accuracy_prev_day_set = request.POST.getlist("data[]['accuracy_prev_day']")

        bulk_predictions_set = []
        duplicate_count = 0
        for i in range(len(prediction_date_set)):
            ## Find if date already exists, and ignore
            if StockPrediction.objects.filter(prediction_date=prediction_date_set[i],
                                              stock_id=request.POST.get('stock_id')).count() > 0:
                duplicate_count += 1
                continue
            stock_prediction = StockPrediction()
            stock_prediction.prediction_date = prediction_date_set[i]
            stock_prediction.high = high_set[i]
            stock_prediction.low = low_set[i]
            stock_prediction.close = close_set[i]
            stock_prediction.stock_id = request.POST.get('stock_id')
            stock_prediction.accuracy_prev_day = accuracy_prev_day_set[i]
            stock_prediction.status = True
            bulk_predictions_set.append(stock_prediction)
        StockPrediction.objects.bulk_create(bulk_predictions_set)
        responseData = {'status': 'success', 'message': 'Data added!', 'total_records': len(bulk_predictions_set),
                        'duplicate_count': duplicate_count}
    return JsonResponse(responseData)


# @method_decorator(admin_login_required, name='dispatch')
def add_stock_predictions(request):
    stock_prediction_id = request.POST.get("stock_prediction_id")
    stock_id = request.POST.get('stock_id')
    stock = Stock.objects.get(pk=stock_id)
    prediction_date = request.POST.get("date")
    high = request.POST.get("high")
    low = request.POST.get("low")
    close = request.POST.get("close")
    accuracy_prev_day = request.POST.get("accuracy_prev_day")
    status = True if request.POST.get("status") == '1' else False

    if stock_prediction_id != '':
        StockPrediction.objects.filter(id=stock_prediction_id).update(prediction_date=prediction_date, high=high,
                                                                      low=low, close=close,
                                                                      accuracy_prev_day=accuracy_prev_day,
                                                                      status=request.POST.get(
                                                                          'status') == '1' and True or False)
    else:
        stock_prediction = StockPrediction()
        stock_prediction.stock_id = stock_id
        stock_prediction.prediction_date = prediction_date
        stock_prediction.high = high
        stock_prediction.low = low
        stock_prediction.close = close
        stock_prediction.accuracy_prev_day = accuracy_prev_day
        stock_prediction.status = status
        stock_prediction.save()

    responseData = {'status': 'success', 'message': 'Data added!'}
    return HttpResponseRedirect(reverse('admin.stock_single', kwargs={'symbol': stock.symbol}))


# @method_decorator(admin_login_required, name='dispatch')
def remove_stock(request):
    if request.method == 'GET':
        if request.GET.get('id'):
            Stock.objects.filter(id=request.GET.get('id')).delete()
            return redirect('admin.index')
    return HttpResponse('Invalid request')


# @method_decorator(admin_login_required, name='dispatch')
def remove_stock_prediction(request):
    if request.method == 'GET':
        if request.GET.get('id'):
            StockPrediction.objects.filter(id=request.GET.get('id')).delete()
            stock = Stock.objects.get(pk=request.GET.get('stock_id'))
            return HttpResponseRedirect(reverse('admin.stock_single', kwargs={'symbol': stock.symbol}))
    return HttpResponse('Invalid request')


def admin_logout(request):
    auth_logout(request)
    return redirect('admin.login')


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj.date())
        return super().default(obj)


# @method_decorator(admin_login_required, name='dispatch')
def get_stock_subscriptions(request):
    data = {}
    stock_obj = Stock.objects.get(symbol=request.GET.get('symbol'))
    if request.POST.get('removed') and request.POST.get('removed') == True:
        data['stock_subscriptions'] = serializers.serialize("json",
                                                            StockSubscription.objects.filter(stock_id=stock_obj.pk,
                                                                                             removed=True),
                                                            cls=LazyEncoder)
    else:
        data['stock_subscriptions'] = serializers.serialize("json",
                                                            StockSubscription.objects.filter(stock_id=stock_obj.pk,
                                                                                             removed=False),
                                                            cls=LazyEncoder)
    print(len(data))
    return JsonResponse(data)
