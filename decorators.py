import jwt
import datetime
import json
import requests

from django.http  import JsonResponse

from my_settings  import SECRET
from users.models import User

def validate_login(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get("Authorization", None)
            if not access_token:
                return JsonResponse({'message': 'login_required'}, status=401)

            access_token_payload = jwt.decode(
                    access_token,
                    SECRET,
                    algorithms="HS256"
                    )

            user = User.objects.get(id=access_token_payload['user_id'])

            access_expiration_delta  = 600
            refresh_expiration_delta = 6000000
            now = datetime.datetime.now().timestamp()
            if now > access_token_payload['iat'] + access_expiration_delta:
                refresh_token_payload = jwt.decode(
                        user.refresh_token,
                        SECRET,
                        algorithms="HS256"
                        )
                if now > refresh_token_payload['iat'] + refresh_expiration_delta:
                    return JsonResponse({'message': 'refresh_token_expired'}, status=401)
                else:
                    access_token = jwt.encode(
                        {
                            'user_id': user.id,
                            'iat'    : datetime.datetime.now().timestamp()
                        },
                        SECRET,
                        algorithm = 'HS256'
                        )
                    return JsonResponse({'message': 'access_token_refreshed', 'access_token': access_token}, status=401)

            request.user = user
            return func(self, request, *args, **kwargs)
        except jwt.DecodeError:
            return JsonResponse({'message': 'invalid_jwt'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'message': 'invalid_user'}, status=401)
    return wrapper
