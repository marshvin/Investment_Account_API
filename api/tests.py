from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import InvestmentAccount, Transaction, UserAccountPermission
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class InvestmentAccountTests(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')

        # Create investment accounts
        self.account1 = InvestmentAccount.objects.create(name='Account 1')
        self.account2 = InvestmentAccount.objects.create(name='Account 2')
        self.account3 = InvestmentAccount.objects.create(name='Account 3')
 

        # Assign permissions
        UserAccountPermission.objects.create(user=self.user1, account=self.account1, permission=UserAccountPermission.VIEW_ONLY)
        UserAccountPermission.objects.create(user=self.user1, account=self.account2, permission=UserAccountPermission.CRUD)
        UserAccountPermission.objects.create(user=self.user1, account=self.account3, permission=UserAccountPermission.POST_ONLY)
        UserAccountPermission.objects.create(user=self.user2, account=self.account2, permission=UserAccountPermission.CRUD)
 

        # Create transactions for testing
        Transaction.objects.create(
            account=self.account1,
            user=self.user1,
            amount=Decimal('100.00'),
            created_at=timezone.now()
        )
        Transaction.objects.create(
            account=self.account2,
            user=self.user1,
            amount=Decimal('200.00'),
            created_at=timezone.now()
        )
        Transaction.objects.create(
            account=self.account2,
            user=self.user1,
            amount=Decimal('50.00'),
            created_at=timezone.now() - timedelta(days=5)
        )
        Transaction.objects.create(
            account=self.account3,
            user=self.user1,
            amount=Decimal('300.00'),
            created_at=timezone.now()
        )
        
    def test_user_belongs_to_multiple_accounts(self):
        """Test that a user can belong to multiple accounts."""
        self.client.login(username='user1', password='pass1')
        url = reverse('investmentaccount-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # user1 has access to all 4 accounts

    def test_account_has_multiple_users(self):
        """Test that an account can have multiple users."""
        # Check that account2 has both user1 and user2
        account2_users = UserAccountPermission.objects.filter(account=self.account2).values_list('user__username', flat=True)
        self.assertIn('user1', account2_users)
        self.assertIn('user2', account2_users)
        
    def test_view_only_permission(self):
        """Test  Account 1 view-only permission cannot post transactions."""
        self.client.login(username='user1', password='pass1')
        url = reverse('transaction-list')
        data = {'account': self.account1.id, 'user': self.user1.id, 'amount': '100.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test that view works
        url = reverse('investmentaccount-detail', args=[self.account1.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_no_permission(self):
        """Test  Account 1 update permission (not allowed)."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('investmentaccount-detail', args=[self.account1.id])
        data = {'name': 'Attempt Update'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_permission(self):
        """Test  Account 2 create permission """
        self.client.force_authenticate(user=self.user1)
        url = reverse('investmentaccount-list')
        data = {'name': 'New Account', 'account': self.account2.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_read_permission(self):
        """Test that read operations are allowed for Account 2 where the user has CRUD permissions."""
        self.client.login(username='user1', password='pass1')

        # Test reading account details
        url = reverse('investmentaccount-detail', args=[self.account2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Account 2')

        # Test reading transactions for the account
        url = reverse('transaction-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        account2_transactions = [t for t in response.data if t['account'] == self.account2.id]
        self.assertEqual(len(account2_transactions), 2)  # There should be 2 transactions for Account 2

        # Verify the contents of the transactions
        amounts = [Decimal(transaction['amount']) for transaction in account2_transactions]
        self.assertIn(Decimal('200.00'), amounts)
        self.assertIn(Decimal('50.00'), amounts)

        # Test reading a specific transaction
        transaction_id = Transaction.objects.filter(account=self.account2).first().id
        url = reverse('transaction-detail', args=[transaction_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['amount']), Decimal('200.00'))
        
    def test_update_permission(self):
        """Test  Account 2 update permission """
        self.client.force_authenticate(user=self.user1)
        url = reverse('investmentaccount-detail', args=[self.account2.id])
        data = {'name': 'Updated Account'}
        response = self.client.put(url, data)
        logger.debug(f"Update response: {response.status_code}")
        logger.debug(f"Update response content: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_permission(self):
        """Test  Account 2 delete permission """
        self.client.force_authenticate(user=self.user1)
        url = reverse('investmentaccount-detail', args=[self.account2.id])
        response = self.client.delete(url)
        logger.debug(f"Delete response: {response.status_code}")
        logger.debug(f"Delete response content: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_account3_post_only_permission(self):
        """Test Account 3 POST_ONLY permission: POST should be allowed, VIEW should not be allowed"""
        self.client.force_authenticate(user=self.user1)
        
        # Test POST permission (should be allowed)
        url = reverse('transaction-list')
        data = {'account': self.account3.id, 'amount': '150.00'}
        response = self.client.post(url, data, format='json')
        logger.debug(f"POST response: {response.status_code}")
        logger.debug(f"POST response content: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test VIEW permission (should not be allowed)
        url = reverse('investmentaccount-detail', args=[self.account3.id])
        response = self.client.get(url)
        logger.debug(f"GET response: {response.status_code}")
        logger.debug(f"GET response content: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



    def test_admin_pull_transactions_for_account(self):
        """Test admin user can pull all transactions for a specific account."""
        self.client.login(username='admin', password='adminpass')

        url = reverse('investmentaccount-admin-transactions', args=[self.account2.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['transactions']), 2)  
        self.assertEqual(response.data['total_balance'], '250.00')  

    def test_admin_pull_transactions_for_user(self):
        """Test admin user can pull all transactions for a specific user in a specific account."""
        self.client.login(username='admin', password='adminpass')

        url = reverse('investmentaccount-admin-transactions', args=[self.account2.id])
        response = self.client.get(url, {'user_id': self.user1.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['transactions']), 2)  # 2 transactions for this user in Account 2
        self.assertEqual(response.data['total_balance'], '250.00')  # 200 + 50

    def test_admin_pull_transactions_with_date_range(self):
        """Test admin user can pull transactions within a specific date range."""
        self.client.login(username='admin', password='adminpass')

        url = reverse('investmentaccount-admin-transactions', args=[self.account2.id])
        start_date = (timezone.now() - timedelta(days=6)).date().isoformat()  # 6 days ago
        end_date = timezone.now().date().isoformat()  # today
        response = self.client.get(url, {'start_date': start_date, 'end_date': end_date}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['transactions']), 2)  # Both transactions fall within the range
        self.assertEqual(response.data['total_balance'], '250.00')  # 200 + 50
