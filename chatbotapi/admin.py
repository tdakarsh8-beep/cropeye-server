from django.contrib import admin
from .models import RateLimit
from datetime import timezone

class RateLimitAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm', 'request_count', 'last_request_time', 'is_rate_limited')
    list_filter = ('user', 'farm', 'last_request_time')
    search_fields = ('user__username', 'farm__name')
    readonly_fields = ('last_request_time', 'request_count', 'is_rate_limited')

    def is_rate_limited(self, obj):
        if obj.last_request_time is None:
            return False
        time_diff = timezone.now() - obj.last_request_time
        return time_diff.total_seconds() < obj.rate_limit_seconds

    is_rate_limited.boolean = True

    def reset_rate_limit(self, request, queryset):
        for rate_limit in queryset:
            rate_limit.request_count = 0
            rate_limit.save()

    reset_rate_limit.short_description = "Reset rate limit counter"
    actions = [reset_rate_limit]

admin.site.register(RateLimit, RateLimitAdmin)
