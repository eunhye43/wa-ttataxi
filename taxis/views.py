import random
from json                       import JSONDecodeError

from django.http                import JsonResponse
from django.views               import View
from django.db.models           import Count, Avg
from django.db.models.functions import Coalesce

from taxis.models               import Location, TaxiDriver, DriverReview
from users.models               import Coupon

class LocationListView(View):
    def get(self, request):
        order_by  = random.choice(['id', '-id', 'location_code', '-location_code', 'name', '-name'])
        locations = Location.objects.annotate(course_count=Count('arrival')).order_by(order_by)
        stations = [
                {
                    "id"          : location.id,
                    "stationCode" : location.location_code,
                    "stationName" : location.name,
                    "longitude"   : location.longitude,
                    "latitude"    : location.latitude,
                    "imageUrl"    : location.image_url,
                    "description" : str(location.course_count)+'여 개의 한강 코스'
                } for location in locations ]

        return JsonResponse({'station': stations}, status=200)

class LocationDetailView(View):
    def get(self, request, location_id):
        try:
            location = Location.objects.get(id=location_id)
            station = {
                        "id"          : location.id,
                        "stationCode" : location.location_code,
                        "stationName" : location.name,
                        "longitude"   : location.longitude,
                        "latitude"    : location.latitude,
                        "imageUrl"    : location.image_url,
                        "description" : str(location.arrival.count())+'여 개의 한강 코스'
                        }

            return JsonResponse({'station': station}, status=200)
        except Location.DoesNotExist:
            return JsonResponse({'message': 'invalid_id'}, status=400)

class TaxiDriverListView(View):
    def get(self, request):
        sort = request.GET.get('sort', None)

        order_method_dict = {
                None : '-review_count',
                'review': '-review_count',
                'rating': '-average_rating'
                }
        sort = None if sort not in order_method_dict else sort
        order_method = order_method_dict[sort]

        taxi_drivers = TaxiDriver.objects.select_related('taxi_company')\
                .annotate(
                        review_count=Count('driverreview'), 
                        average_rating=Coalesce(Avg('driverreview__rating'), 0.0)
                        )\
                .order_by(order_method)
        drivers = [
                {
                    "id"                    : driver.id,
                    "name"                  : driver.name,
                    "taxi_company_name"     : driver.taxi_company.name,
                    "taxi_company_logo_url" : driver.taxi_company.logo_url,
                    "profile_url"           : driver.profile_url,
                    "review_count"          : driver.review_count,
                    "average_rating"        : driver.average_rating,
                    "introduction"          : driver.introduction
                } for driver in taxi_drivers ]

        return JsonResponse({'drivers': drivers}, status=200)

class TaxiDriverDetailView(View):
    def get(self, request, driver_id):
        try:
            driver      = TaxiDriver.objects.get(id=driver_id)
            driver_info = {
                        "id"                    : driver.id,
                        "name"                  : driver.name,
                        "taxi_company_name"     : driver.taxi_company.name,
                        "taxi_company_logo_url" : driver.taxi_company.logo_url,
                        "profile_url"           : driver.profile_url,
                        "review_count"          : driver.driverreview_set.count(),
                        "average_rating"        : driver.driverreview_set.aggregate(average_rating=Coalesce(Avg('rating'), 0.0))['average_rating'],
                        "introduction"          : driver.introduction
                        }

            return JsonResponse({'driver': driver_info}, status=200)
        except TaxiDriver.DoesNotExist:
            return JsonResponse({'message': 'invalid_id'}, status=400)

class CouponListView(View):
    def get(self, request):
        order_by = random.choice(['id', '-id', 'name', '-name'])
        coupons  = Coupon.objects.order_by(order_by)
        banners  = [
                {
                    "imageUrl": coupon.image_url
                } for coupon in coupons ]
        return JsonResponse({'banner': banners}, status=200)

