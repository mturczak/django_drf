from Django_API.models import CustomUser

class CustomUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                request.user = CustomUser.objects.get(username=request.user.username)
            except CustomUser.DoesNotExist:
                pass
        response = self.get_response(request)
        return response