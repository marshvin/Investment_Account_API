from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestmentAccountViewSet, TransactionViewSet


router = DefaultRouter()
router.register(r'investmentaccounts', InvestmentAccountViewSet, basename='investmentaccount')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
   
    path('', include(router.urls)),
]
