# api/views.py
import requests
from rest_framework import generics, permissions, status
from .models import Crypto, Transaction, UserProfile
from .serializers import CryptoSerializer, TransactionSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.utils import timezone



class CryptoListView(generics.ListCreateAPIView):
    queryset = Crypto.objects.all()
    serializer_class = CryptoSerializer
    permission_classes = [permissions.AllowAny]


class CryptoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Crypto.objects.all()
    serializer_class = CryptoSerializer


class UserProfileListView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permissions_classes = [permissions.AllowAny]


class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class TransactionListView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permissions_classes = [permissions.AllowAny]


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class FetchMixedTransactions(APIView):
    def get(self, request):
        try:
            price_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
            price_data = requests.get(price_url).json()

            btc_price = price_data.get("bitcoin", {}).get("usd", 0)
            eth_price = price_data.get("ethereum", {}).get("usd", 0)

            btc_crypto, _ = Crypto.objects.get_or_create(
                symbol="BTC",
                defaults={
                    "name": "Bitcoin",
                    "price": btc_price or 0,
                    "market_cap": 0,
                    "volume_24h": 0,
                },
            )

            eth_crypto, _ = Crypto.objects.get_or_create(
                symbol="ETH",
                defaults={
                    "name": "Ethereum",
                    "price": eth_price or 0,
                    "market_cap": 0,
                    "volume_24h": 0,
                },
            )

            btc_url = "https://api.blockcypher.com/v1/btc/main/txs"
            eth_blocks = [1000000, 1100000, 1200000, 1300000, 1400000]
            eth_data = []
            for block_num in eth_blocks:
                block = requests.get(f"https://api.blockcypher.com/v1/eth/main/blocks/{block_num}").json()
                if block.get("txids"):
                    tx_hash = block["txids"][0]
                    tx = requests.get(f"https://api.blockcypher.com/v1/eth/main/txs/{tx_hash}").json()
                    eth_data.append(tx)

            all_saved = []

            btc_data = requests.get(btc_url).json()[:5]

            all_saved = []

            for tx in btc_data:
                obj = Transaction.objects.create(
                    crypto=btc_crypto,
                    hash=tx.get("hash"),
                    chain="BTC",
                    sender=(
                        tx.get("inputs")[0]["addresses"][0]
                        if tx.get("inputs")
                        else "unknown"
                    ),
                    receiver=(
                        tx.get("outputs")[0]["addresses"][0]
                        if tx.get("outputs")
                        else "unknown"
                    ),
                    amount=tx.get("total", 0) / 100000000,  # sat → BTC
                    timestamp=datetime.utcnow(),
                )

                all_saved.append(
                    {
                        "hash": obj.hash,
                        "chain": obj.chain,
                        "sender": obj.sender,
                        "receiver": obj.receiver,
                        "amount": obj.amount,
                    }
                )

            for tx in eth_data:
                obj = Transaction.objects.create(
                    crypto=eth_crypto,
                    hash=tx.get("hash"),
                    chain="ETH",
                    sender=(
                        tx.get("inputs")[0]["addresses"][0]
                        if tx.get("inputs")
                        else "unknown"
                    ),
                    receiver=(
                        tx.get("outputs")[0]["addresses"][0]
                        if tx.get("outputs")
                        else "unknown"
                    ),
                    amount=int(tx.get("total", 0)) / 1e18,  # wei → ETH
                    timestamp=datetime.utcnow(),
                )

                all_saved.append(
                    {
                        "hash": obj.hash,
                        "chain": obj.chain,
                        "sender": obj.sender,
                        "receiver": obj.receiver,
                        "amount": obj.amount,
                    }
                )

            return Response(all_saved, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    
