import json

from django.test  import TestCase, Client

from taxis.models import Location, TaxiDriver, TaxiCompany, DriverReview
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
