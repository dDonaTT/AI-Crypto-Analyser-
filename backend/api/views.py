# api/views.py
import requests
from rest_framework import generics, permissions, status, filters
from .models import Crypto, Transaction, UserProfile
from .serializers import CryptoSerializer, TransactionSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Max, Avg
from .ai_module import detect_anomaly


class CryptoListView(generics.ListCreateAPIView):
    queryset = Crypto.objects.all()
    serializer_class = CryptoSerializer
    permission_classes = [permissions.AllowAny]


class CryptoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Crypto.objects.all()
    serializer_class = CryptoSerializer
class CryptoTrendView(APIView):
    def get(self, request):
        try:
            cryptos = ["bitcoin", "ethereum"]
            trend_data = {}
            
            for crypto in cryptos:
                url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart"
                params = {
                    "vs_currency": "usd",
                    "days": 7
                }
                resp = requests.get(url, params=params).json()
                prices = [price[1] for price in resp.get("prices", [])]
                if not prices:
                    trend_data[crypto] = "No data"
                    continue
                start_price = prices[0]
                end_price = prices[-1]
                change_percent = ((end_price - start_price) / start_price) * 100

                if change_percent > 1.5:
                    trend= "Bullish"
                elif change_percent < 1.5:
                    trend = "Bearish"
                else:
                    trend = "Neutral"
                trend_data[crypto] = {
                    "start_price": start_price,
                    "end_price": end_price,
                    "change_percent": round(change_percent,2),
                    "trend": trend
                }
            return Response(trend_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filter_fields = {
        "chain": ["exact"],
        "amount": ["gte", "lte"],
        "timestamp": ["gte", "lte"],
    }
    search_fields = ["sender", "receiver", "hash"]
    ordering_fields = ["-timestamp"]
    def perform_create(self, serializer):
        transaction = serializer.save()
        tx_dict = {
            "amount": float(transaction.amount),
            "timestamp": transaction.timestamp,
        }
        result = detect_anomaly(tx_dict)
        if result["is_anomaly"]:
            transaction.is_anomaly = True
            transaction.risk_score = result["risk_score"]
            transaction.save()       


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionAnalyticsView(APIView):
    def get(self, request):
        try:
            total_amount = (
                Transaction.objects.aggregate(total=Sum("amount"))["total"] or 0
            )

            btc_qs = Transaction.objects.filter(crypto__symbol="BTC")
            eth_qs = Transaction.objects.filter(crypto__symbol="ETH")

            total_btc_amount = btc_qs.aggregate(total=Sum("amount"))["total"] or 0
            total_eth_amount = eth_qs.aggregate(total=Sum("amount"))["total"] or 0

            largest_transaction = (
                Transaction.objects.order_by("-amount")
                .values("hash", "amount", "chain", "sender", "receiver", "timestamp")
                .first()
                or {}
            )

            average_amount = (
                Transaction.objects.aggregate(avg=Avg("amount"))["avg"] or 0
            )

            latest_10_transactions = list(
                Transaction.objects.order_by("-timestamp").values(
                    "hash", "amount", "chain", "sender", "receiver", "timestamp"
                )[:10]
            )

            data = {
                "summary": {
                    "total_amount": total_amount,
                    "btc_count": btc_qs.count(),
                    "eth_count": eth_qs.count(),
                },
                "totals": {
                    "total_btc_amount": total_btc_amount,
                    "total_eth_amount": total_eth_amount,
                },
                "largest_transaction": largest_transaction,
                "averages": {
                    "average_amount": average_amount,
                },
                "latest_10_transactions": latest_10_transactions,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


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
                block = requests.get(
                    f"https://api.blockcypher.com/v1/eth/main/blocks/{block_num}"
                ).json()
                if block.get("txids"):
                    tx_hash = block["txids"][0]
                    tx = requests.get(
                        f"https://api.blockcypher.com/v1/eth/main/txs/{tx_hash}"
                    ).json()
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
