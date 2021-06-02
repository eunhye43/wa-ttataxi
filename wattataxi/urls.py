"""wattataxi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
<<<<<<< HEAD

from django.urls import path, include

urlpatterns = [
    path('taxis', include('taxis.urls')),
    path('users', include('users.urls')),
    path('orders', include('orders.urls')),
]
=======
from django.urls import path, include

urlpatterns = [
    path("taxis", include("taxis.urls")),
    ]
>>>>>>> cd1c762 (ADD: 검색 및 필터링, 정렬 기능 구현 완료)
