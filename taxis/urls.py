from django.urls import path

from taxis.views import LocationListView, TaxiDriverListView, LocationDetailView, TaxiDriverDetailView, CouponListView, ReviewView

urlpatterns = [
    path('/locations', LocationListView.as_view()),
    path('/taxidrivers', TaxiDriverListView.as_view()),
    path('/locations/<int:location_id>', LocationDetailView.as_view()),
    path('/taxidrivers/<int:driver_id>', TaxiDriverDetailView.as_view()),
    path('/coupons', CouponListView.as_view()),
    path('/reviews', ReviewView.as_view()),
    path('/reviews/<int:review_id>', ReviewView.as_view()),
]

