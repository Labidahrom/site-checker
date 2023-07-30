from site_checker.models import Notification

class NotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            notifications = Notification.objects.filter(is_active=True)
            request.notifications = notifications
        response = self.get_response(request)
        return response
