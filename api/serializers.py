from rest_framework import serializers
from .models import InvestmentAccount, Transaction, UserAccountPermission

class InvestmentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentAccount
        fields = ['id', 'name', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Transaction
        fields = ['id', 'account', 'user', 'amount', 'created_at']
        read_only_fields = ['created_at']

class UserAccountPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccountPermission
        fields = ['user', 'account', 'permission']
