from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from farms.models import Farm  # Assuming the farm app has been created

User = get_user_model()

class FarmChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='chats')
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['user', 'farm']),  # Indexed to speed up queries for a specific user-farm pair
            models.Index(fields=['timestamp']),  # Indexed for fast chronological queries
        ]

    def __str__(self):
        return f"Chat between {self.user.username} and {self.farm.name} at {self.timestamp}"

class UserChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_histories')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='user_chat_histories')
    chat_history = models.JSONField(default=list)  # Store the chat history as a list of messages
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'farm'])  # Indexed to speed up user-farm specific history retrieval
        ]
        
    def __str__(self):
        return f"Chat history for {self.user.username} on farm {self.farm.name}"

# Model to store and cache responses from the chatbot to avoid re-generating the same responses.
class LLMResponseCache(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='llm_responses')
    farm_name = models.CharField(max_length=255)
    prompt = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'farm_name']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"LLM Response for {self.user.username} on farm {self.farm_name}"

class RateLimit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rate_limits')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='rate_limits')
    last_request_time = models.DateTimeField(auto_now=True)
    request_count = models.IntegerField(default=0)  # Tracks the number of requests a user has made in the time frame
    
    RATE_LIMIT_THRESHOLD = 10  # Max requests allowed within the time window (per minute)
    RATE_LIMIT_WINDOW = timezone.timedelta(minutes=1)  # 1 minute time window

    def is_rate_limited(self):
        """Check if the user has exceeded the rate limit within the defined window."""
        time_diff = timezone.now() - self.last_request_time
        
        if time_diff > self.RATE_LIMIT_WINDOW:
            # Reset counter if the window has passed
            self.request_count = 0
            # Update the last request time to the current time
            self.last_request_time = timezone.now()
            self.save()  # Save changes to reset counter

        if self.request_count >= self.RATE_LIMIT_THRESHOLD:
            return True  # The user is rate-limited

        return False

    def increment_request_count(self):
        """Increment the request count for the user."""
        self.request_count += 1
        self.save()

    def __str__(self):
        return f"Rate limit for {self.user.username} on farm {self.farm.name}"
