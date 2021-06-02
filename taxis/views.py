import random
import json
import datetime
from json                       import JSONDecodeError

from django.http                import JsonResponse
from django.views               import View
from django.db.models           import Count, Avg, Q
from django.db.models.functions import Coalesce

from taxis.models               import Location, TaxiDriver, DriverReview, Schedule, Course
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

class TaxiListView(View):
    def get(self, request):
        departure_location_name  = request.GET.get('departure_location_name', None)
        arrival_location_name    = request.GET.get('arrival_location_name', None)
        seat_type                = request.GET.get('seat_type')
        seat_remain              = request.GET.get('seat_remain')
        departure_date_string    = request.GET.get('departure_date')
    
        departure_time           = request.GET.get('departure_time', '1900-01-01 23:00')
        price                    = request.GET.get('price', 60000)
        taxi_company             = request.GET.getlist('taxi_company', ['Dasul Taxi', 'Taxi Choi-gging', 'Art Transportation', 'Lama 운수', 'DaMo taxi', 'Muy bien Trans'])
        sort                     = request.GET.get('sort', '-price')

        sort_list = {
            'dep_time'      : '-course__departure_time',
            'price'         : '-price'
        }
        sort_string    = sort_list[sort]

        departure_date = datetime.datetime.strptime(departure_date_string, "%Y-%m-%d")

        courses = Course.objects.filter(
            Q(departure_location__name=departure_location_name) 
            & Q(arrival_location__name=arrival_location_name))

        schedules = Schedule.objects.filter(
              Q(date=departure_date) 
            & Q(seat_type__name=seat_type)
            & Q(course_id__in=[course.id for course in courses]) 
            & Q(seat_remain__gte = seat_remain)
            & Q(price__lte=price)
            & Q(course__taxi_company__name__in = taxi_company)
            & Q(course__departure_time__lte = departure_time)).order_by(sort_string)

        total_result = []

        for schedule in schedules:
            result = {
                'id'   : schedule.id,
                'price'       : schedule.price,
                'seat_remain' : schedule.seat_remain,
                'date'        : schedule.date,
                'courses' : {
                    'departure_time'          : schedule.course.departure_time,
                    'arrival_time'            : schedule.course.arrival_time,
                    'taxi_code'               : schedule.course.taxi_code,
                    'arrival_location_id'     : schedule.course.arrival_location.id,
                    'arrival_location_name'   : schedule.course.arrival_location.name,
                    'arrival_location_code'   : schedule.course.arrival_location.location_code,
                    'departure_location_id'   : schedule.course.departure_location.id,
                    'departure_location_name' : schedule.course.departure_location.name,
                    'departure_location_code' : schedule.course.departure_location.location_code,
                    'taxi_company'            : schedule.course.taxi_company.name,
                    'taxi_company_url'        : schedule.course.taxi_company.logo_url
                },
                'seat_type' : {
                    'seat_name' : schedule.seat_type.name,
                    'sale_rate' : schedule.seat_type.sale_rate
                    },
                'taxi_driver' : {
                    'taxi_driver_name' : schedule.taxi_driver.name,
                    'taxi_company'     : schedule.taxi_driver.taxi_company.name,
                    'profile_url'      : schedule.taxi_driver.profile_url,
                    'introduction'     : schedule.taxi_driver.introduction
                    }
            }
            total_result.append(result)
        return JsonResponse({"Message" : total_result}, status = 200)
