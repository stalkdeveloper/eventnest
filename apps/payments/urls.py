from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('events/<slug:slug>/checkout/', views.initiate_checkout, name='checkout'),
    path('payments/success/',            views.payment_success,   name='payment_success'),
    path('payments/webhook/',            views.razorpay_webhook,  name='razorpay_webhook'),
]
