from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models

class InvestmentAccount(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now) 
    users = models.ManyToManyField(User, through='UserAccountPermission')

class UserAccountPermission(models.Model):
    VIEW_ONLY = 'view'
    CRUD = 'crud'
    POST_ONLY = 'post'

    PERMISSION_CHOICES = [
        (VIEW_ONLY, 'View Only'),
        (CRUD, 'CRUD'),
        (POST_ONLY, 'Post Only'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES)

    class Meta:
        unique_together = ['user', 'account']

class Transaction(models.Model):
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
