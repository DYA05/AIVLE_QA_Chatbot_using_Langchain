# myapp/middleware.py

from django.utils.deprecation import MiddlewareMixin

class CustomSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 세션이 아직 생성되지 않았거나 세션 키가 없는 경우
        if not request.session.session_key:
            # 세션 데이터 설정하여 세션 생성 강제
            request.session['initial'] = True
            request.session.save()
            # 세션 키 확인
            session_key = request.session.session_key
            print(f'New session created with session key: {session_key}')

    def process_response(self, request, response):
        return response
