from django.urls import path
from .views import DepositView, PaymentView, TipView

app_name = 'payments'

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('pay/', PaymentView.as_view(), name='payment'),
    path('tip/', TipView.as_view(), name='tip'),
]