
from django.db import models

class Crypto(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    market_cap = models.BigIntegerField()

    def __str__(self):
        return self.name
