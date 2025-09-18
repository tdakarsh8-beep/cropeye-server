# chatbotapi/serializers.py

from rest_framework import serializers
from .models import FarmChat
from farms.models import Farm

class FarmChatSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.name', read_only=True)

    class Meta:
        model = FarmChat
        fields = [
            'id',
            'user',
            'farm',
            'farm_name',
            'message',
            'response',
            'timestamp',
        ]
        read_only_fields = ['id', 'user', 'response', 'timestamp']
