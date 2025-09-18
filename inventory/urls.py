from django.urls import path, include
from rest_framework_nested import routers
from .views import InventoryItemViewSet, InventoryTransactionViewSet

router = routers.DefaultRouter()
router.register('inventory', InventoryItemViewSet)
router.register('transactions', InventoryTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 