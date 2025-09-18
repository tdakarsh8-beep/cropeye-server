# chatbotapi/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmChatViewSet

router = DefaultRouter()
router.register(r'chats', FarmChatViewSet, basename='farmchat')

urlpatterns = [
    path('', include(router.urls)),
]
