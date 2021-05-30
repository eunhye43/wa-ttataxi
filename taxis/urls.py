from django.urls import path

from taxis.views import LocationListView, TaxiDriverListView, LocationDetailView, TaxiDriverDetailView, CouponListView

urlpatterns = [
    path('/locations', LocationListView.as_view()),
    path('/taxidrivers', TaxiDriverListView.as_view()),
    path('/locations/<int:location_id>', LocationDetailView.as_view()),
    path('/taxidrivers/<int:driver_id>', TaxiDriverDetailView.as_view()),
    path('/coupons', CouponListView.as_view()),
]

