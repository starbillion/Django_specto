from cart.models import Item
from django.urls import reverse
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import json
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from monthdelta import monthdelta
from payments import get_payment_model, RedirectNeeded
from django.contrib.auth.decorators import login_required
from mainsite.custom_decorators import anonymous_required
from django.core import serializers
from datetime import datetime, timedelta
from django.views.generic import FormView, TemplateView
from stocks.models import Stock
from subscriptions.models import StockSubscription
from django.http import (
    HttpResponse, HttpResponseRedirect
)
from payment.models import (
    UserBillingAddress, Transaction
)
from cities_light.models import Country, Region, City
import time
from cart.cart import Cart
from paypal.standard.forms import PayPalPaymentsForm
from subscriptions.models import Subscription
import braintree
from mainsite.helpers import (
    get_user_agent, get_request_ip,
    generate_random_string
)
from django.utils.timezone import localdate
braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id=settings.BRAINTREE_MERCHANT_ID,
                                  public_key=settings.BRAINTREE_PUBLIC_KEY,
                                  private_key=settings.BRAINTREE_PRIVATE_KEY)


@method_decorator(login_required, name='dispatch')
class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'checkout/index.html'

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['user_profile'] = self.request.user.userprofile
        context['cart'] = self.get_cart_data()
        context['countries'] = Country.objects.all()
        self.request.session['braintree_client_token'] = braintree.ClientToken.generate()
        return context

    def get_cart_data(self):
        cart_data = []
        cart = Cart(self.request)
        for item in cart:
            stock = Stock.objects.get(pk=item.product.stock_id)
            cart_data.append(
                {'plan_duration': item.product.plan_duration, 'quantity': item.quantity, 'price': item.total_price,
                 'stock': stock})
        return cart_data


def process_checkout(request):
    # Braintree customer info
    # You can, for sure, use several approaches to gather customer infos
    # For now, we'll simply use the given data of the user instance
    customer_kwargs = {
        "first_name": request.POST.get('first_name'),
        "last_name": request.POST.get('last_name'),
        "email": request.POST.get('email'),
    }
    # Create a new Braintree customer
    # In this example we always create new Braintree users
    # You can store and re-use Braintree's customer IDs, if you want to
    result = braintree.Customer.create(customer_kwargs)
    if not result.is_success:
        data = {}
        # Ouch, something went wrong here
        # I recommend to send an error report to all admins
        # , including ``result.message`` and ``request.user.email``

        # context = self.get_context_data()
        # We re-generate the form and display the relevant braintree error
        # context.update({
        # 	'form': self.get_form(self.get_form_class()),
        data['braintree_error'] = u'{} {}'.format(result.message, _('Please get in contact.'))
        # })
        # return self.render_to_response(context)
        return JsonResponse({'message': 'Deadd!! Unable to create rbaintree customer', 'data': data})

    # If the customer creation was successful you might want to also
    # add the customer id to your user profile
    customer_id = result.customer.id

    """
    Create a new transaction and submit it.
    I don't gather the whole address in this example, but I can
    highly recommend to do that. It will help you to avoid any
    fraud issues, since some providers require matching addresses
    """
    ccc = request.POST.get('country')
    print(ccc)
    country = Country.objects.get(pk=request.POST.get('country'))
    address_dict = {
        "first_name": request.POST.get('first_name'),
        "last_name": request.POST.get('last_name'),
        "street_address": request.POST.get('address_line_1'),
        "extended_address": request.POST.get('address_line_2', ''),
        "locality": request.POST.get('city'),
        "region": request.POST.get('state_or_region'),
        "postal_code": request.POST.get('postal_code'),
        "country_code_alpha2": country.code2,
        "country_code_alpha3": country.code3,
        "country_name": country.name_ascii,
        # "country_code_numeric": '356',
    }

    # You can use the form to calculate a total or add a static total amount
    # I'll use a static amount in this example
    result = braintree.Transaction.sale({
        # "customer_id": customer_id,
        "amount": request.POST.get('total_price'),
        "payment_method_nonce": request.POST.get('payment_method_nonce'),
        "descriptor": {
            # Definitely check out https://developers.braintreepayments.com/reference/general/validation-errors/all/python#descriptor
            "name": "DjSpect*Stock forecast",
        },
        "billing": address_dict,
        # "shipping": address_dict,
        "options": {
            # Use this option to store the customer data, if successful
            'store_in_vault_on_success': True,
            # Use this option to directly settle the transaction
            # If you want to settle the transaction later, use ``False`` and later on
            # ``braintree.Transaction.submit_for_settlement("the_transaction_id")``
            'submit_for_settlement': True,
        },
    })

    cart_data_as_list = []
    cart = Cart(request)
    for item in cart:
        stock = Stock.objects.get(pk=item.product.stock_id)
        # cart_data_as_list.append({'stock_name': stock.name, 'stock_symbol': stock.symbol,
        #                           'total_price': float(item.total_price),
        #                           'plan_duration': float(item.product.plan_duration)})
        cart_data_as_list.append({'stock_symbol': stock.symbol,
                                  'plan_duration': item.product.plan_duration,
                                  'total_price': float(item.total_price)})
    cart_data_as_json = json.dumps(cart_data_as_list)

    # if not result.is_success:
    if not result.is_success:
        # Card could've been declined or whatever
        # I recommend to send an error report to all admins
        # , including ``result.message`` and ``request.user.email``
        data = {}
        # context = self.get_context_data()
        # context.update({
        # 	'form': self.get_form(self.get_form_class()),
        data[
            'braintree_error'] = 'Your payment could not be processed. Please check your input or use another payment method and try again.'
        data['msg'] = result.message
        trans_id = generate_random_string(10)
        data['transaction_id'] = trans_id
        # return self.render_to_response(context)
        # Saving transaction
        trans = Transaction.objects.create(
            user=request.user,
            transaction_id=trans_id,
            transaction_type='braintree',
            cart_details=cart_data_as_json,
            user_agent=get_user_agent(request),
            ip=get_request_ip(request),
            status=False
        )
        return HttpResponseRedirect(reverse('payment.transaction_error'), data)

    # Finally there's the transaction ID
    # You definitely want to send it to your database
    data = {}
    transaction_id = result.transaction.id
    data['transaction_id'] = transaction_id
    subscribed = []
    cart = Cart(request)

    # calculating duratin and price paid for storing to subscription table
    temp = {}
    for item in cart_data_as_list:
        if item['stock_symbol'] in temp:
            temp[item['stock_symbol']]['plan_duration'] += item['plan_duration']
            temp[item['stock_symbol']]['total_price'] += item['total_price']
        else:
            temp[item['stock_symbol']] = {'plan_duration': int(item['plan_duration']),
                                          'total_price': float(item['total_price'])}

        # subscribed.append({"symbol": stock_symbol,
        #                    "stock_name": Stock.objects.get(symbol=stock_symbol).name,
        #                    "duration": value['plan_duration'],
        #                    "date_from": datetime.now(),
        #                    "date_end": datetime.now()+monthdelta(int(value['plan_duration'])),
        #                    "total_price": value['total_price']})
    # for item in cart:
    #     stock_subscription_id = StockSubscription.objects.get(id=item.object_id, stock_id=item.product.stock_id,
    #                                                           plan_duration=item.product.plan_duration, removed=False)
    #     stock_subscription, created = Subscription.objects.get_or_create(user=request.user,
    #                                                                      stock_subscription=stock_subscription_id)
    #     stock_subscription.price = item.total_price
    #     stock_subscription.subscription_ends = datetime.now() + timedelta(days=item.product.plan_duration * 30)
    #     stock_subscription.status = True
    #     stock_subscription.save()
    #     subscribed.append(stock_subscription)

    # Register subscribed stock in StockSubscription model
    data['subscribed'] = subscribed
    cart.clear()

    # Saving transaction
    trans = Transaction.objects.create(
        user=request.user,
        transaction_id=result.transaction.id,
        transaction_type='braintree',
        cart_details=cart_data_as_json,
        user_agent=get_user_agent(request),
        ip=get_request_ip(request),
        status=True
    )
    # storing to subscription table
    for stock_symbol, value in temp.items():
        stock_id = Stock.objects.get(symbol=stock_symbol).id

        # if current stock exists already in Subscription table
        if Subscription.objects.filter(stock_id=stock_id).exists():
            temp_sub = Subscription.objects.filter(stock_id=stock_id).order_by("-subscription_ends")[0]

            t = Subscription.objects.create(user=request.user,
                                            stock_id=stock_id,
                                            transaction=trans,
                                            status=True,
                                            is_hidden=False,
                                            subscription_started=temp_sub.subscription_ends,
                                            subscription_ends=temp_sub.subscription_ends + monthdelta(int(value['plan_duration'])),
                                            purchased_months=value['plan_duration'],
                                            total_price=value['total_price'])
        # not
        else:
            t = Subscription.objects.create(user=request.user,
                                            stock_id=stock_id,
                                            transaction=trans,
                                            status=True,
                                            is_hidden=False,
                                            subscription_started=datetime.now(),
                                            subscription_ends=datetime.now() + monthdelta(int(value['plan_duration'])),
                                            purchased_months=value['plan_duration'],
                                            total_price=value['total_price'])
        subscribed.append(t)

    data['transaction_id'] = result.transaction.id

    # Saving the billing address of the customer
    if not request.POST.get('not_remember_billing_address'):
        billing_address_dict = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'address_line_1': request.POST.get('address_line_1'),
            'address_line_2': request.POST.get('address_line_2', ''),
            'postal_code': request.POST.get('postal_code'),
            'country': country.name_ascii,
            'state': request.POST.get('state_or_region'),
            'city': request.POST.get('locality'),
        }
        if not request.POST.get('not_remember_billing_address'):
            person, created = UserBillingAddress.objects.update_or_create(user=request.user,
                                                                          defaults=billing_address_dict)

    # Now you can send out confirmation emails or update your metrics
    # or do whatever makes you and your customers happy :)
    return render(request, 'payment/success.html', data)
    return HttpResponseRedirect(reverse('payment.transaction_success'), data)


"""
Generating client token for braintree payments
"""


def generate_client_token(request):
    amount = request.POST.get('price')
    user = request.user
    user_braintree_customer_id = user.userprofile.braintree_customer_id
    a_customer_id = ''
    if not user_braintree_customer_id:
        result = braintree.Customer.create({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company": "DjSpect",
            "email": user.email,
            # "phone": "312.555.1234",
            # "fax": "614.555.5678",
            # "website": "www.example.com"
        })
        if result.is_success:
            user.userprofile.braintree_customer_id = result.customer.id
            user.userprofile.save()
            a_customer_id = user.userprofile.braintree_customer_id
        else:
            a_customer_id = user.userprofile.braintree_customer_id
    if not user.userprofile.client_token:
        client_token = braintree.ClientToken.generate({
            "customer_id": a_customer_id
        })
        user.userprofile.client_token = client_token
        user.userprofile.save()
    else:
        client_token = user.userprofile.client_token

    variables = {'amount': amount, 'client_token': client_token}
    return JsonResponse(variables)


# return render(request, 'checkout.html',variables)


@method_decorator(login_required, name='dispatch')
class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'checkout/cart.html'

    def get_context_data(self, **kwargs):
        cart_data = []
        cart = Cart(self.request)
        for item in cart:
            stock = Stock.objects.get(pk=item.product.stock_id)
            cart_data.append(
                {'plan_duration': item.product.plan_duration, 'quantity': item.quantity, 'price': item.total_price,
                 'stock': stock})
        context = super(CartView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['cart'] = cart_data
        return context


def cart_remove_item(request):
    cart = Cart(request)
    product = StockSubscription.objects.get(stock_id=request.GET.get('product'),
                                            plan_duration=request.GET.get('duration'), removed=False)
    cart.remove(product)
    return HttpResponseRedirect(reverse('payment.cart'))


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return HttpResponseRedirect(reverse('payment.cart'))


def paypal_return_view(request):
    return JsonResponse({'status': 1, 'message': 'Bingo! paypal return view', 'data': request})


def paypal_cancel_return_view(request):
    return JsonResponse({'status': 1, 'message': 'Bingo! Paypal cancel return view', 'data': request})


def transaction_error(request):
    data = {}
    return render(request, 'payment/error.html', data)


def transaction_success(request):
    data = {}
    return render(request, 'payment/success.html', data)
