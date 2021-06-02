from django.urls import path

from orders.views import BookView

urlpatterns = [
    path('', BookView.as_view()),
    path('/<int:order_id>', BookView.as_view()),
]
