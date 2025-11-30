from django.urls import path
from .views import (
    CryptoListView,
    CryptoDetailView,
    TransactionListView,
    TransactionDetailView,
    TransactionAnalyticsView,
    UserProfileListView,
    UserProfileDetailView,
    FetchMixedTransactions
)
from .views_auth import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("cryptos/", CryptoListView.as_view(), name="crypto-list"),
    path("cryptos/<int:pk>/", CryptoDetailView.as_view(), name="crypto-detail"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path(
        "transactions/<int:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    path("transactions/fetch-mixed/", FetchMixedTransactions.as_view(), name="fetch_mixed"),
    path("transactions/analytics/", TransactionAnalyticsView.as_view(), name="transaction-analytics"),

    path("profiles/", UserProfileListView.as_view(), name="profile-list"),
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profiles/<int:pk>/", UserProfileDetailView.as_view(), name="profile-detail"),
]
