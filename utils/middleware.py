import traceback
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime
from utils.slack import send_error_slack

class SlackExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        start_time = getattr(request, "_start_time", datetime.now())  # 없으면 현재 시간
        request._start_time = start_time  # 혹시나 없을 경우 기록

        request.api_name = f"{request.method} {request.path}"  # API 이름 추정

        # 슬랙 오류 전송
        send_error_slack(request, request.api_name, start_time)
        return None
