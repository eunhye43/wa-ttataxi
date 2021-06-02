import random
import json
from json                       import JSONDecodeError

from django.http                import JsonResponse
from django.views               import View
from django.db.models           import Count, Avg
from django.db.models.functions import Coalesce

from taxis.models               import Location, TaxiDriver, DriverReview
from users.models               import Coupon
from decorators                 import validate_login

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

class ReviewView(View):
    def get(self, request):
        try:
            driver_id = request.GET.get('driver_id', None)

            reviews = DriverReview.objects.filter(taxi_driver_id=driver_id).select_related('user').order_by('-id')

            results = [
                    {
                        "review_id"        : review.id,
                        "user_name"        : review.user.name,
                        "user_profile_url" : review.user.profile_url if review.user.profile_url else "https://image.flaticon.com/icons/png/512/1808/1808120.png",
                        "rating"           : review.rating,
                        "review"           : review.review
                    } for review in reviews ]

            return JsonResponse({'message': 'success', 'reviews': results}, status=200)
        except JSONDecodeError:
            return JsonResponse({'message': 'invalid_input'}, status=400)
        except DriverReview.DoesNotExist:
            return JsonResponse({'message': 'invalid_driver_id'}, status=400)
        except ValueError:
            return JsonResponse({'message': 'invalid_input'}, status=400)

    @validate_login
    def post(self, request):
        try:
            data      = json.loads(request.body)
            rating    = data.get('rating', None)
            text      = data.get('text', None)
            driver_id = data.get('driver_id', None)
            user      = request.user

            if not driver_id or not text or not rating:
                return JsonResponse({'message': 'no_input'}, status=400)

            if not TaxiDriver.objects.filter(id=driver_id).exists():
                return JsonResponse({'message': 'invalid_input'}, status=400)

            driver_review = DriverReview.objects.create(
                    taxi_driver_id = driver_id,
                    user           = user,
                    rating         = rating,
                    review         = text
                    )

            return JsonResponse({'message': 'success'}, status=201)
        except KeyError:
            return JsonResponse({'message':'invalid_input'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'message':'invalid_input'}, status=400)
        except ValueError:
            return JsonResponse({'message': 'invalid_input'}, status=400)

    @validate_login
    def delete(self, request, review_id):
        try:
            review    = DriverReview.objects.get(id=review_id)
            user      = request.user

            if review.user != user:
                return JsonResponse({'message':'invalid_user'}, status=401)

            review.delete()

            return JsonResponse({'message':'success'}, status=201)
        except KeyError:
            return JsonResponse({'message':'invalid_input'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'message':'invalid_input'}, status=400)
        except DriverReview.DoesNotExist:
            return JsonResponse({'message':'invalid_input'}, status=400)
        except ValueError:
            return JsonResponse({'message': 'invalid_input'}, status=400)
