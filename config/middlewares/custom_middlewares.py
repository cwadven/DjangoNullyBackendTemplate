class RequestUserToMemberMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.member = request.user
        request.guest = None
        response = self.get_response(request)
        return response
