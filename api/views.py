from decimal import Decimal
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.decorators import action
from .models import InvestmentAccount, Transaction, UserAccountPermission
from .serializers import InvestmentAccountSerializer, TransactionSerializer
from .permissions import AccountPermission
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
class InvestmentAccountViewSet(viewsets.ModelViewSet):
    queryset = InvestmentAccount.objects.all()
    serializer_class = InvestmentAccountSerializer
    permission_classes = [AccountPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return InvestmentAccount.objects.all()
        return InvestmentAccount.objects.filter(users=user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def admin_transactions(self, request, pk=None):
        user_id = request.query_params.get('user_id')  
        account_id = pk  

        # Filter transactions based on user_id and account_id
        transactions = Transaction.objects.filter(account_id=account_id)
        
        if user_id:
            transactions = transactions.filter(user_id=user_id)
        
        # Filter transactions by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            if start_date and end_date:
            
                start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
                end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
                transactions = transactions.filter(created_at__range=[start_datetime, end_datetime])

        total_balance = transactions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        return Response({
            'transactions': TransactionSerializer(transactions, many=True).data,
            'total_balance': f"{total_balance:.2f}"
        })


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AccountPermission]

    def perform_create(self, serializer):
        logger.debug("Perform create method called")
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        logger.debug(f"Getting queryset for user: {user}")
        
        # Get all accounts the user has permissions for
        user_account_permissions = UserAccountPermission.objects.filter(user=user)
        allowed_account_ids = user_account_permissions.values_list('account_id', flat=True)
        
        # Filter transactions based on these accounts
        queryset = Transaction.objects.filter(account_id__in=allowed_account_ids)
        
        logger.debug(f"Queryset count: {queryset.count()}")
        return queryset
