import json
import jwt
import datetime
import requests
import bcrypt
import string
import random
from json.decoder      import JSONDecodeError

from django.http       import JsonResponse
from django.views      import View

from users.models      import User, KakaoToken
from my_settings       import SECRET
from users.validations import Validation
from decorators        import validate_login

KAKAO_REST_API_KEY  = "bf3992782086681b3a5421eaa743704d"
MAX_PASSWORD_LENGTH = 15

class UserInfoView(View):
    @validate_login
    def get(self, request):
        user = request.user
        user_info = {
                'user_name'   : user.name,
                'user_email'  : user.email,
                'profile_url' : user.profile_url if user.profile_url else "https://image.flaticon.com/icons/png/512/1808/1808120.png"
                }
        return JsonResponse({'message': 'success', 'user_info': user_info}, status=200)

class SignupView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data['name']
            email = data['email']
            password = data['password']

            if not Validation.validate_email(self, email):
                return JsonResponse({'message':'invalid_email'}, status=400)

            if not Validation.validate_password(self, password):
                return JsonResponse({'message':'invalid_password'}, status=400)
            
            if not Validation.validate_name(self, name):
                return JsonResponse({'message':'invalid_name'}, status=400)
            
            if not Validation.validate_duplication(self, email):
                return JsonResponse({'message':'already_exists', 'email':email}, status=400)

            password = bcrypt.hashpw(
                    password.encode('utf-8'),
                    bcrypt.gensalt()
                    ).decode('utf-8')

            user = User.objects.create(
                    name     = name,
                    password = password,
                    email    = email
                    )

            return JsonResponse({'created_user': user.name}, status=201)
        except KeyError:
            return JsonResponse({'message': 'key_error'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'message': 'no_body'}, status=400)

class SigninView(View):
    def post(self, request):
        try:
            data  = json.loads(request.body)
            email = data['email']

            user = User.objects.get(email=email)

            if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
                return JsonResponse({'message':'invalid_password'}, status=401)

            access_token = jwt.encode(
                    {
                        'user_id': user.id,
                        'iat'    : datetime.datetime.now().timestamp()
                    },
                    SECRET,
                    algorithm = 'HS256'
            )
            refresh_token = jwt.encode(
                    {
                        'user_id': user.id,
                        'iat'    : datetime.datetime.now().timestamp()
                    },
                    SECRET,
                    algorithm = 'HS256'
            )

            user.refresh_token = refresh_token
            user.save()

            return JsonResponse({'access_token': access_token}, status=201)
        except KeyError:
            return JsonResponse({'message': 'key_error'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'message': 'no_body'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'message': 'invalid_email'}, status=400)

class KakaoSigninView(View):
    def post(self, request):
        try:
            kakao_access_token  = json.loads(request.body).get("access_token", None)
            kakao_refresh_token = json.loads(request.body).get("refresh_token", None)
            
            if not kakao_access_token or not kakao_refresh_token:
                return JsonResponse({'message': 'kakaotoken_required'}, status=401)

            USER_INFO_API   = 'https://kapi.kakao.com/v2/user/me'
            kakao_user_info = requests.get(USER_INFO_API, headers={'Authorization': 'Bearer ' + kakao_access_token}).json()
            
            if kakao_user_info.get("msg") == "this access token does not exist":
                return JsonResponse({'message': 'invalid_jwt'}, status=401)
            
            if kakao_user_info.get("msg") == "this access token is already expired":
                return JsonResponse({'message': 'login_again'}, status=401)

            kakao_id    = kakao_user_info["id"]
            name        = kakao_user_info["kakao_account"]["profile"]["nickname"]
            email       = kakao_user_info["kakao_account"]["email"]
            profile_url = kakao_user_info["kakao_account"]["profile"]["thumbnail_image_url"]

            if User.objects.filter(kakao_id=kakao_id).exists():
                user = User.objects.get(kakao_id=kakao_id)
            elif User.objects.filter(email=email).exists():
                return JsonResponse({'message':'already_exists', 'email':email}, status=400)
            else:
                letters         = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
                random_string   = ''.join(random.choice(letters) for _ in range(MAX_PASSWORD_LENGTH))
                random_password = bcrypt.hashpw(
                            random_string.encode('utf-8'),
                            bcrypt.gensalt()
                            ).decode('utf-8')
                user = User.objects.create(
                        name = name,
                        email = email,
                        password = random_password,
                        kakao_id = kakao_user_info.get("id"),
                        profile_url = profile_url
                        )

            kakao_token_string  = kakao_access_token + ' ' + kakao_refresh_token

            if KakaoToken.objects.filter(user=user).exists():
                kakao_token = KakaoToken.objects.get(user=user)
                kakao_token.token = kakao_token_string
                kakao_token.save()
            else:
                kakao_token = KakaoToken.objects.create(
                        user  = user,
                        token = kakao_token_string
                        )

            access_token = jwt.encode(
                    {
                        'user_id': user.id,
                        'iat'    : datetime.datetime.now().timestamp()
                    },
                    SECRET,
                    algorithm = 'HS256'
            )
            refresh_token = jwt.encode(
                    {
                        'user_id': user.id,
                        'iat'    : datetime.datetime.now().timestamp()
                    },
                    SECRET,
                    algorithm = 'HS256'
            )

            user.refresh_token = refresh_token
            user.save()

            return JsonResponse({'message': 'success', 'user': user.name, 'access_token': access_token}, status=201)
        except KeyError:
            return JsonResponse({'message': 'key_error'}, status=400)


class LogoutView(View):
    def post(self, request):
        try:
            access_token = json.loads(request.body).get("access_token", None)

            if not access_token:
                return JsonResponse({'message': 'no_jwt'}, status=401)

            access_token_payload = jwt.decode(
                    access_token,
                    SECRET,
                    algorithms="HS256"
                    )

            user = User.objects.get(id=access_token_payload['user_id'])
            user.refresh_token = None
            user.save()

            kakao_token = KakaoToken.objects.get(user=user)
            kakao_access_token = kakao_token.token.split()[0]
            
            LOGOUT_API  = 'https://kapi.kakao.com/v1/user/logout'
            logout_user = requests.get(LOGOUT_API, headers={'Authorization': 'Bearer ' + kakao_access_token})

            return JsonResponse({'message': 'success'}, status=201)
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message': 'invalid_token'}, status=400)
        except KakaoToken.DoesNotExist:
            return JsonResponse({'message': 'success'}, status=201)
