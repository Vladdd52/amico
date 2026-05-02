from django.shortcuts import render
from django_ratelimit.exceptions import Ratelimited

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            import logging
            logger = logging.getLogger('django')
            logger.error(f"Rate limit exceeded for IP: {request.META.get('REMOTE_ADDR')}")
            
            response = render(request, '429.html', status=429)
            
            if request.headers.get('HX-Request'):
                response['HX-Retarget'] = 'body'
                response['HX-Reswap'] = 'innerHTML'
                response.status_code = 200 
                
            return response
        return None
