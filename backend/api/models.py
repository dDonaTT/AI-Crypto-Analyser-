
from django.db import models
from django.contrib.auth.models import User

class Crypto(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10 ,unique=True)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    market_cap = models.DecimalField(max_digits=20, decimal_places=4)
    volume_24h = models.DecimalField(max_digits=20, decimal_places=2,default=0.0)
    change_24h = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-market_cap']
        verbose_name = 'Crypto'
        verbose_name_plural = 'Cryptocurrencies'

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('analyst','Analyst'),
        ('user', 'User'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

class Transaction(models.Model):
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE, related_name='transactions')
    hash = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    sender = models.CharField(max_length=100)
    reciever = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
