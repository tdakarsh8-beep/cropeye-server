from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q

from .models import FarmChat, UserChatHistory, LLMResponseCache, RateLimit
from farms.models import Farm
from .serializers import FarmChatSerializer
from .utils import generate_response  # Your LLM integration logic

class FarmChatViewSet(viewsets.ModelViewSet):
    queryset = FarmChat.objects.all()
    serializer_class = FarmChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-timestamp')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='chat')
    def chat_with_farm(self, request):
        user = request.user
        farm_id = request.data.get("farm_id")
        message = request.data.get("message")

        if not farm_id or not message:
            return Response({"error": "farm_id and message are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            return Response({"error": "Farm not found."}, status=status.HTTP_404_NOT_FOUND)

        # Rate limiting
        rate_limit, _ = RateLimit.objects.get_or_create(user=user, farm=farm)
        if rate_limit.is_rate_limited():
            return Response({"error": "Rate limit exceeded. Please wait a while before sending more messages."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        rate_limit.increment_request_count()

        # Optional: use LLMResponseCache to avoid reprocessing same prompt
        cached = LLMResponseCache.objects.filter(
            user=user, farm_name=farm.name, prompt=message
        ).first()

        if cached:
            response_text = cached.response
        else:
            prompt = f"Farm Info: {farm.description}\nUser: {message}"
            response_text = generate_response(prompt)

            # Cache the response
            LLMResponseCache.objects.create(
                user=user,
                farm_name=farm.name,
                prompt=message,
                response=response_text
            )

        # Save chat to DB
        FarmChat.objects.create(user=user, farm=farm, message=message, response=response_text)

        # Update chat history
        chat_history, _ = UserChatHistory.objects.get_or_create(user=user, farm=farm)
        chat_history.chat_history.append({
            "role": "user", "content": message,
            "response": response_text,
            "timestamp": timezone.now().isoformat()
        })
        chat_history.save()

        return Response({"message": message, "response": response_text})
