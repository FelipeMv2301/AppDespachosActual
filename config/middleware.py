class DomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.domain = request.META['HTTP_HOST']
        return self.get_response(request)
