from django.urls import path
from .views import CryptoListView, TransactionListView, UserProfileListView

urlpatterns = [
    path('cryptos/', CryptoListView.as_view(), name='crypto-list'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('profiles/', UserProfileListView.as_view(), name='profile-list'),
]
