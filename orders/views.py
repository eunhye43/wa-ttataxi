import json

from django.http       import JsonResponse
from django.views      import View

from decorators        import validate_login
from orders.models     import Order, Status, ScheduleOrder
from taxis.models      import Schedule

STATUS_BOOK     = 1
STATUS_FINISHED = 2
STATUS_CANCLED  = 3
TAX             = 8800

class BookView(View):
    @validate_login
    def post(self, request):
        try:
            data               = json.loads(request.body)
            passenger_number   = data.get('passenger_number', None)
            going_schedule_id  = data.get('going_schedule_id', None)
            coming_schedule_id = data.get('coming_schedule_id', None)
            user               = request.user
            
            schedule_ids = [ schedule_id for schedule_id in (going_schedule_id, coming_schedule_id) if schedule_id ]

            for schedule_id in schedule_ids:
                if passenger_number > Schedule.objects.get(id=schedule_id).seat_remain:
                    return JsonResponse({'message': 'no_seat_remain'}, status=401)

            order = Order.objects.create(user=user, status_id=STATUS_BOOK)

            for schedule_id in schedule_ids:
                schedule_orders = ScheduleOrder.objects.create(
                        order            = order,
                        schedule_id      = schedule_id,
                        tax              = TAX,
                        passenger_number = passenger_number
                        ) 

                schedule  = Schedule.objects.get(id=schedule_id)
                schedule.seat_remain -= passenger_number
                schedule.save()

            return JsonResponse({'message': 'success'}, status=201)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'message': 'no_body'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'key_error'}, status=400)
        except Schedule.DoesNotExist:
            return JsonResponse({'message': 'invalid_id'}, status=400)

    @validate_login
    def get(self, request):
        try:
            user   = request.user
            orders = Order.objects.filter(user=user).prefetch_related('scheduleorder_set__schedule__course').order_by('-created_at')
            
            results = [
                    {
                        'order_id'                 : order.id,
                        'round_trip'               : '왕복' if order.scheduleorder_set.count() == 2 else '편도',
                        'departure_location'       : order.scheduleorder_set.all()[0].schedule.course.departure_location.name,
                        'departure_location_code'  : order.scheduleorder_set.all()[0].schedule.course.departure_location.location_code,
                        'arrival_location'         : order.scheduleorder_set.all()[0].schedule.course.arrival_location.name,
                        'arrival_location_code'   : order.scheduleorder_set.all()[0].schedule.course.arrival_location.location_code,
                        'departure_date'           : order.scheduleorder_set.all()[0].schedule.date.strftime('%m-%d'),
                        'comeback_date'            : order.scheduleorder_set.all()[1].schedule.date.strftime('%m-%d') if order.scheduleorder_set.count() == 2 else None,
                        'passenger_number'         : order.scheduleorder_set.all()[0].passenger_number,
                        'going_taxi_company_name'  : order.scheduleorder_set.all()[0].schedule.course.taxi_company.name,
                        'going_taxi_company_logo'  : order.scheduleorder_set.all()[0].schedule.course.taxi_company.logo_url,
                        'going_price'              : order.scheduleorder_set.all()[0].schedule.price,
                        'coming_taxi_company_name' : order.scheduleorder_set.all()[1].schedule.course.taxi_company.name if order.scheduleorder_set.count() == 2 else None,
                        'coming_taxi_company_logo' : order.scheduleorder_set.all()[1].schedule.course.taxi_company.logo_url if order.scheduleorder_set.count() == 2 else None,
                        'coming_price'             : order.scheduleorder_set.all()[1].schedule.price if order.scheduleorder_set.count() == 2 else None
                    } for order in orders ]

            return JsonResponse({'result': results}, status=200)
        except IndexError:
            return JsonResponse({'message': 'data_error'}, status=400)


    @validate_login
    def delete(self, request, order_id):
        try:
            user = request.user
            
            order = Order.objects.get(id=order_id)
            if order.user_id != user.id:
                return JsonResponse({'message': 'invalid_user'}, status=400)

            schedule_orders = order.scheduleorder_set.all()

            for schedule_order in schedule_orders:
                schedule = schedule_order.schedule
                schedule.seat_remain += schedule_order.passenger_number
                schedule.save()
                schedule_order.delete()

            order.delete()

            return JsonResponse({'message': 'success'}, status=201)
        except Order.DoesNotExist:
            return JsonResponse({'message': 'invalid_id'}, status=400)
