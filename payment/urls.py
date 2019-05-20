from django.conf.urls import include, url
from .views import(
	CheckoutView, CartView,
	cart_remove_item, cart_clear,
	paypal_cancel_return_view, paypal_return_view,
	generate_client_token, process_checkout,
	transaction_success, transaction_error,
)

urlpatterns = [
	# Payments handling
	url(r'^process-checkout/$', process_checkout, name='payment.process_checkout'),
	url(r'^generate-client-token/$', generate_client_token, name='payment.generate_client_token'),
	url(r'^cart_remove_item/$', cart_remove_item, name='payment.cart_remove_item'),
	url(r'^cart_clear/$', cart_clear, name='payment.cart_clear'),
	url(r'^checkout/$', CheckoutView.as_view(), name='payment.checkout'),
	url(r'^cart/$', CartView.as_view(), name='payment.cart'),
	url(r'^paypal/', include('paypal.standard.ipn.urls')),
	url(r'^paypal-return-view/', paypal_return_view, name='paypal_return_view'),
	url(r'^paypal-cancel-return-view/', paypal_cancel_return_view, name='paypal_cancel_return_view'),
	url(r'^success/$', transaction_success, name='payment.transaction_success'),
	url(r'^error/$', transaction_error, name='payment.transaction_error'),
]