# api/views.py
from rest_framework import generics
from .models import Crypto
from .serializers import CryptoSerializer

class CryptoListView(generics.ListCreateAPIView):
    queryset = Crypto.objects.all()
    serializer_class = CryptoSerializer
