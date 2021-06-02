import json
import bcrypt

from django.test  import TestCase, Client

from taxis.models import Location, TaxiDriver, TaxiCompany, DriverReview, Course, SeatType, Schedule
from users.models import User

class LocationListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Location.objects.create(
                id            = 1,
                name          = 'test',
                longitude     = 0.0,
                latitude      = 0.0,
                location_code = 'test',
                image_url     = 'test'
        )

    def test_locationlist_get_success(self):
        client = Client()
        response = client.get('/taxis/locations')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    'station': [
                        {
                            'id'          : 1,
                            'stationCode' : 'test',
                            'stationName' : 'test',
                            'longitude'   : '0.00000',
                            'latitude'    : '0.00000',
                            'imageUrl'    : 'test',
                            'description' : '0여 개의 한강 코스'
                        }
                    ]
                }
        )

class LocationDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Location.objects.create(
                id            = 1,
                name          = 'test',
                longitude     = 0.0,
                latitude      = 0.0,
                location_code = 'test',
                image_url     = 'test'
        )

    def test_locationdetail_get_success(self):
        client = Client()
        response = client.get('/taxis/locations/1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    'station': 
                        {
                            'id'          : 1,
                            'stationCode' : 'test',
                            'stationName' : 'test',
                            'longitude'   : '0.00000',
                            'latitude'    : '0.00000',
                            'imageUrl'    : 'test',
                            'description' : '0여 개의 한강 코스'
                        }
                }
        )

    def test_locationdetail_get_invalid_id(self):
        client = Client()
        response = client.get('/taxis/locations/0')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                {
                    'message': 'invalid_id'
                }
        )

class TaxiDriverListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(
                id       = 1,
                name     = 'user name',
                email    = 'user email',
                password = 'user password'
        )

        taxi_company = TaxiCompany.objects.create(
                id       = 1,
                name     = 'company name',
                logo_url = 'company logo'
        )

        taxi_driver = TaxiDriver.objects.create(
                id           = 1,
                name         = 'driver name',
                taxi_company = taxi_company,
                profile_url  = 'driver profile',
                introduction = 'driver introduction',
        )

        review_1 = DriverReview.objects.create(
                id          = 1,
                taxi_driver = taxi_driver,
                user        = user,
                rating      = 1,
                review      = '싫어요'
        )

        review_2 = DriverReview.objects.create(
                id          = 2,
                taxi_driver = taxi_driver,
                user        = user,
                rating      = 5,
                review      = '좋아요'
        )

    def test_taxidriverlist_get_success(self):
        client = Client()
        response = client.get('/taxis/taxidrivers')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    'drivers': [
                        {
                            'id': 1,
                            'name': 'driver name',
                            'taxi_company_name': 'company name',
                            'taxi_company_logo_url': 'company logo',
                            'profile_url': 'driver profile',
                            'review_count': 2,
                            'average_rating': 3.0,
                            'introduction': 'driver introduction'
                        }
                    ]
                }
        )

class TaxiDriverDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(
                id       = 1,
                name     = 'user name',
                email    = 'user email',
                password = 'user password'
        )

        taxi_company = TaxiCompany.objects.create(
                id       = 1,
                name     = 'company name',
                logo_url = 'company logo'
        )

        taxi_driver = TaxiDriver.objects.create(
                id           = 1,
                name         = 'driver name',
                taxi_company = taxi_company,
                profile_url  = 'driver profile',
                introduction = 'driver introduction',
        )

        review_1 = DriverReview.objects.create(
                id          = 1,
                taxi_driver = taxi_driver,
                user        = user,
                rating      = 1,
                review      = '싫어요'
        )

        review_2 = DriverReview.objects.create(
                id          = 2,
                taxi_driver = taxi_driver,
                user        = user,
                rating      = 5,
                review      = '좋아요'
        )

    def test_taxidriverdetail_get_success(self):
        client = Client()
        response = client.get('/taxis/taxidrivers/1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    'driver': 
                        {
                            'id': 1,
                            'name': 'driver name',
                            'taxi_company_name': 'company name',
                            'taxi_company_logo_url': 'company logo',
                            'profile_url': 'driver profile',
                            'review_count': 2,
                            'average_rating': 3.0,
                            'introduction': 'driver introduction'
                        }
                }
        )

    def test_taxidriverdetail_get_invalid_id(self):
        client = Client()
        response = client.get('/taxis/taxidrivers/0')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                {
                    'message': 'invalid_id'
                }
        )

class ReviewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
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

        taxi_company = TaxiCompany.objects.create(
                id       = 1,
                name     = 'company name',
                logo_url = 'company logo'
        )

        taxi_driver = TaxiDriver.objects.create(
                id           = 1,
                name         = 'driver name',
                taxi_company = taxi_company,
                profile_url  = 'driver profile',
                introduction = 'driver introduction',
        )

        review_1 = DriverReview.objects.create(
                id          = 1,
                taxi_driver = taxi_driver,
                user        = user,
                rating      = 1,
                review      = '싫어요'
        )

        review_2 = DriverReview.objects.create(
                id          = 2,
                taxi_driver = taxi_driver,
                user        = user,
                rating      = 5,
                review      = '좋아요'
        )

    def test_review_get_success(self):
        client = Client()
        response = client.get('/taxis/reviews?driver_id=1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    'message': 'success',
                    'reviews': [
                        {
                            'review_id': 2,
                            'user_name': 'user',
                            'user_profile_url': 'https://image.flaticon.com/icons/png/512/1808/1808120.png',
                            'rating': 5,
                            'review': '좋아요'
                        },
                        {
                            'review_id': 1,
                            'user_name': 'user',
                            'user_profile_url': 'https://image.flaticon.com/icons/png/512/1808/1808120.png',
                            'rating': 1,
                            'review': '싫어요'
                        }
                   ]
                }
        )

    def test_review_get_value_error(self):
        client = Client()
        response = client.get('/taxis/reviews?driver_id=a')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 
                {
                    'message': 'invalid_input'
                }
        )

    def test_review_post_success(self):
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
                'driver_id' : 1,
                'rating'    : 5,
                'text'      : 'test'
        }

        response = client.post('/taxis/reviews', json.dumps(data), **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), 
                {
                    'message': 'success'
                }
        )

    def test_review_post_invalid_input(self):
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
                'driver_id' : 9,
                'rating'    : 5,
                'text'      : 'test'
        }

        response = client.post('/taxis/reviews', json.dumps(data), **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 
                {
                    'message': 'invalid_input'
                }
        )

    def test_review_delete_success(self):
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

        response = client.delete('/taxis/reviews/1', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), 
                {
                    'message': 'success'
                }
        )

    def test_review_delete_invalid_input(self):
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

        response = client.delete('/taxis/reviews/9', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 
                {
                    'message': 'invalid_input'
                }
        )
class TaxilistTest(TestCase):
    def setUp(self):
        Location.objects.create(
            id = 1,
            name = "망원", 
            longitude = 0,
            latitude = 0,
            location_code = "MWN",
            image_url = "dasfkdasjf444"

        )
        Location.objects.create(
            id = 4,
            name = "선유도",
            longitude = 0,
            latitude = 0,
            location_code = "SUD",
            image_url = '333safsfsa'

        )

        TaxiCompany.objects.create(
            id = 1,
            name = "Dasul Taxi",
            logo_url = 'https://younggeon-myawsbucket.s3.ap-northeast-2.amazonaws.com/logo_dasul.png'
        )

        Course.objects.create(
            id=1,
            departure_time="1990-01-01 22:00",
            arrival_time="1990-01-01 23:00",
            taxi_code="DT030", 
            arrival_location_id=4, 
            departure_location_id=1, 
            taxi_company_id=1
            ),

        SeatType.objects.create(
            id = 1, 
            name="비즈니스석", 
            sale_rate=2.0
            ),

        TaxiDriver.objects.create(
            id=1, 
            name="이다슬", 
            profile_url="https://trello-attachments.s3.amazonaws.com/60ab36332dad093c8d65aaca/60ae0bf22e177364dda07287/ead58f19c51327bfb4108d83f8024cce/image.jpeg", 
            introduction="와따택시에 사랑 한스푼.. 웃음 두 스푼.. 행복 세스푼.. 더해 손님들의 귀갓길이 행복이 가득허길 바랍니다. 만수무강 하시기를.", 
            taxi_company_id=1
            ),

        Schedule.objects.create(
            id=1, 
            price=30000.00, 
            seat_remain=9, 
            date="2021-08-27", 
            course_id=1, 
            seat_type_id=1, 
            taxi_driver_id=1
        )
    def tearDown(self):
        Schedule.objects.all().delete()
        TaxiDriver.objects.all().delete()
        SeatType.objects.all().delete()
        Course.objects.all().delete()

    def test_productlist_get_success(self):
        client = Client()
        # print(Schedule.objects.get(id=1).course.departure_location.name)
        response = client.get('/taxis?departure_location_name=망원&arrival_location_name=선유도&seat_type=비즈니스석&departure_date=2021-08-27&arrival_date=2021-08-27&price=30000&taxi_company=Dasul Taxi&sort=price&seat_remain=9&departure_time=1900-01-01 22:00')
        self.assertEqual(response.json(), {
            'Message' : [{
                'id'   : 1,
                'price'       : 30000,
                'seat_remain' : 9,
                'date'        : "2021-08-27",
                'courses' : {
                    'departure_time'          : "1900-01-01 22:00",
                    'arrival_time'            : "1990-01-01 23:00",
                    'taxi_code'               : "DT001",
                    'arrival_location_id'     : 4,
                    'arrival_location_name'   : "선유도",
                    'arrival_location_code'   : "SUD",
                    'departure_location_id'   : 1,
                    'departure_location_name' : "망원",
                    'departure_location_code' : "MWN",
                    'taxi_company'            : "Dasul Taxi",
                    'taxi_company_url'        : "https://younggeon-myawsbucket.s3.ap-northeast-2.amazonaws.com/logo_dasul.png"
                },
                'seat_type' : {
                    'seat_name' : "비즈니스석",
                    'sale_rate' : "2.0"
                    },
                'taxi_driver' : {
                    'taxi_driver_name' : "이다슬",
                    'taxi_company'     : "Dasul Taxi",
                    'profile_url'      : "https://trello-attachments.s3.amazonaws.com/60ab36332dad093c8d65aaca/60ae0bf22e177364dda07287/ead58f19c51327bfb4108d83f8024cce/image.jpeg",
                    'introduction'     : "등으로 짊어지면 짐이 되지만 가슴으로 안으면 사랑이 된다고 합니다.. 비가오나 눈이 오나 다술택시는 멈추지 않습니다. 언제든 찾아주십쇼. 감사합니다."
                    }
        }]
    })
        self.assertEqual(response.status_code, 200)