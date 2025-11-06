# api/views.py
from rest_framework import generics, permissions
from .models import Crypto, Transaction, UserProfile
from .serializers import CryptoSerializer, TransactionSerializer, UserProfileSerializer


class CryptoListView(generics.ListCreateAPIView):
    queryset = Crypto.objects.all()
    serializer_class = CryptoSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileListView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permissions_classes = [permissions.AllowAny]
class TransactionListView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permissions_classes = [permissions.AllowAny]
