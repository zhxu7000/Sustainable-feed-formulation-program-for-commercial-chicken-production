from django.http import JsonResponse
import traceback
import logging

class GlobalExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # 获取异常的详细信息
            error_info = traceback.format_exc()
            # 使用 logging 将异常信息写入日志文件
            logging.error(error_info)
            # 返回 JSON 响应
            return JsonResponse({
                'status': 'error',
                'message': 'Internal Server Error',
                'detail': str(e)
            }, status=500)


