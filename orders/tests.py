import json
import bcrypt
import datetime

from django.test   import TestCase, Client

from taxis.models  import TaxiCompany, TaxiDriver, Course, Schedule, Location, SeatType
from users.models  import User
from orders.models import Order, ScheduleOrder, Status

test_date = datetime.datetime.now()

class OrderTest(TestCase):
    def setUp(self):
        password = bcrypt.hashpw(
                'P@ssw0rd'.encode('utf-8'),
                bcrypt.gensalt()
                ).decode('utf-8')

        user = User.objects.create(
                id       = 1,
                name     = 'user',
                email    = 'user@example.com',
                password = password
        )

        location = Location.objects.create(
                id            = 1,
                name          = 'test',
                longitude     = 0.0,
                latitude      = 0.0,
                location_code = 'test',
                image_url     = 'test'
        )

        seat_type = SeatType.objects.create(
                id = 1,
                name = 'test',
                sale_rate = 0.0
        )

        taxi_company = TaxiCompany.objects.create(
                id       = 1,
                name     = 'test',
                logo_url = 'test'
        )

        taxi_driver = TaxiDriver.objects.create(
                id           = 1,
                name         = 'test',
                taxi_company = taxi_company,
                profile_url  = 'test',
                introduction = 'test',
        )

        course = Course.objects.create(
                id                 = 1,
                departure_location = location,
                arrival_location   = location,
                departure_time     = test_date,
                arrival_time       = test_date,
                taxi_code          = 'test',
                taxi_company       = taxi_company
        )

        schedule = Schedule.objects.create(
                id          = 1,
                course      = course,
                price       = 10000,
                seat_type   = seat_type,
                seat_remain = 10,
                taxi_driver = taxi_driver,
                date        = test_date
        )

        status = Status.objects.create(
                id   = 1,
                name = 'test'
        )

        order = Order.objects.create(
                id         = 1,
                user       = user,
                status     = status,
                created_at = test_date
        )

        schedule_order1 = ScheduleOrder.objects.create(
                schedule         = schedule,
                order            = order,
                passenger_number = 1,
                tax              = 0
        )

        schedule_order2 = ScheduleOrder.objects.create(
                schedule         = schedule,
                order            = order,
                passenger_number = 1,
                tax              = 0
        )

    def tearDown(self):
        TaxiCompany.objects.all().delete()
        TaxiDriver.objects.all().delete()
        Course.objects.all().delete()
        Schedule.objects.all().delete()
        Location.objects.all().delete()
        SeatType.objects.all().delete()
        User.objects.all().delete()
        Order.objects.all().delete()
        ScheduleOrder.objects.all().delete()
        Status.objects.all().delete()

    def test_order_get_success(self):
        client = Client()

        user = {
                'email': 'user@example.com',
                'password': 'P@ssw0rd'
        }

        access_token = client.post('/users/signin', json.dumps(user), content_type='application/json').json().get('access_token')

        headers = {
                'HTTP_Authorization': access_token,
                'content_type': 'application/json'
        }

        response = client.get('/orders', **headers)

        result_date = test_date.strftime('%m-%d')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
                {
                    'result': [
                        {
                            'order_id'                 : 1,
                            'round_trip'               : '왕복',
                            'departure_location'       : 'test',
                            'departure_location_code'  : 'test',
                            'arrival_location'         : 'test',
                            'arrival_location_code'    : 'test',
                            'departure_date'           : result_date,
                            'comeback_date'            : result_date,
                            'passenger_number'         : 1,
                            'going_taxi_company_name'  : 'test',
                            'going_taxi_company_logo'  : 'test',
                            'going_price'              : '10000.000',
                            'coming_taxi_company_name' : 'test',
                            'coming_taxi_company_logo' : 'test',
                            'coming_price'             : '10000.000'
                        }
                    ]
                }
        )


    def test_order_post_success(self):
        client = Client()

        user = {
                'email': 'user@example.com',
                'password': 'P@ssw0rd'
        }

        access_token = client.post('/users/signin', json.dumps(user), content_type='application/json').json().get('access_token')

        headers = {
                'HTTP_Authorization': access_token,
                'content_type': 'application/json'
        }

        data = {
                'passenger_number'   : 1,
                'going_schedule_id'  : 1,
                'coming_schedule_id' : 1
        }

        response = client.post('/orders', json.dumps(data), **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), 
                {
                    'message': 'success'
                }
        )

    def test_order_post_invalid_id(self):
        client = Client()

        user = {
                'email': 'user@example.com',
                'password': 'P@ssw0rd'
        }

        access_token = client.post('/users/signin', json.dumps(user), content_type='application/json').json().get('access_token')

        headers = {
                'HTTP_Authorization': access_token,
                'content_type': 'application/json'
        }

        data = {
                'passenger_number'   : 1,
                'going_schedule_id'  : 2,
                'coming_schedule_id' : 2
        }

        response = client.post('/orders', json.dumps(data), **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 
                {
                    'message': 'invalid_id'
                }
        )

    def test_order_delete_success(self):
        client = Client()

        user = {
                'email': 'user@example.com',
                'password': 'P@ssw0rd'
        }

        access_token = client.post('/users/signin', json.dumps(user), content_type='application/json').json().get('access_token')

        headers = {
                'HTTP_Authorization': access_token,
                'content_type': 'application/json'
        }

        response = client.delete('/orders/1', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), 
                {
                    'message': 'success'
                }
        )

    def test_order_delete_invalid_id(self):
        client = Client()

        user = {
                'email': 'user@example.com',
                'password': 'P@ssw0rd'
        }

        access_token = client.post('/users/signin', json.dumps(user), content_type='application/json').json().get('access_token')

        headers = {
                'HTTP_Authorization': access_token,
                'content_type': 'application/json'
        }

        response = client.delete('/orders/2', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 
                {
                    'message': 'invalid_id'
                }
        )
