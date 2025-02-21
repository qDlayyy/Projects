import time
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class RequestResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request, *args, **kwds):
        start_time = time.time()

        logger.info(f'\nIncoming Request: {request.method} {request.get_full_path()}')

        try:
            response = self.get_response(request)
        
        except Exception as e:
            logger.error(f'Error occured: {e}')

            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

        duration = time.time() - start_time
        logger.info(f'Outgoing Response: {response.status_code} Duration: {duration:.6f} seconds\n')

        response = self.get_response(request)
        return response


class GetHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        headers = request.headers

        logger.info(f'HEADERS: {headers}')

        response = self.get_response(request)
        return response
