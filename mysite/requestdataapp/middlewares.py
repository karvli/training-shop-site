from datetime import datetime, timedelta

from django.http import HttpRequest, HttpResponse


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip = ''
        self.last_response_time = None
        self.responses_history = {}

    def __call__(self, request: HttpRequest):
        ip = request.META.get('REMOTE_ADDR')

        if ip is not None:
            # Слишком частые запросы - чаще, чем раз в 5 секунду
            time_delta = 5
            now = datetime.now()
            border_time = now - timedelta(seconds=time_delta)

            last_time = self.responses_history.get(ip, border_time)
            self.responses_history[ip] = now

            if last_time > border_time:
                content = (f'Too many requests.'
                           f' Passed since last request: {(last_time - border_time).seconds} seconds.'
                           f' Wait for {time_delta} seconds.')

                # "Too Many Requests", "(«"Слишком много запросов"
                return HttpResponse(content, status=429)

        return self.get_response(request)