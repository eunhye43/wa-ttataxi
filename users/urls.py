from django.urls import path

from users.views import SignupView, SigninView, KakaoSigninView, UserInfoView, LogoutView

urlpatterns = [
    path('/userinfo', UserInfoView.as_view()),
    path('/signup', SignupView.as_view()),
    path('/signin', SigninView.as_view()),
    path('/kakaosignin', KakaoSigninView.as_view()),
    path('/logout', LogoutView.as_view()),
]
