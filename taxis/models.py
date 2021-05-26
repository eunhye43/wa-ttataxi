from django.db import models

class Course(models.Model):
    departure_location = models.ForeignKey("Location", on_delete=models.CASCADE, related_name='departure')
    arrival_location   = models.ForeignKey("Location", on_delete=models.CASCADE, related_name='arrival')
    departure_time     = models.DateTimeField()
    arrival_time       = models.DateTimeField()
    taxi_code          = models.CharField(max_length=45)
    taxi_company       = models.ForeignKey("TaxiCompany", on_delete=models.CASCADE)

    class Meta:
        db_table = "courses"

class Schedule(models.Model):
    course             = models.ForeignKey("Course", on_delete=models.CASCADE)
    price              = models.DecimalField(max_digits=13, decimal_places=3)
    seat_type          = models.ForeignKey("SeatType", on_delete=models.CASCADE)
    seat_remain        = models.IntegerField()
    taxi_driver        = models.ForeignKey("TaxiDriver", on_delete=models.CASCADE)
    date               = models.DateTimeField()

    class Meta:
        db_table  = "schedules"

class SeatType(models.Model):
    name               = models.CharField(max_length=45)
    sale_rate          = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        db_table  = "seat_types"

class Location(models.Model):
    name               = models.CharField(max_length=45)
    longitude          = models.DecimalField(max_digits=8, decimal_places=5)
    latitude           = models.DecimalField(max_digits=8, decimal_places=5)
    location_code      = models.CharField(max_length=20)
    image_url          = models.URLField(max_length=2000, default='')

    class Meta:
        db_table = "locations"

class TaxiCompany(models.Model):
    name               = models.CharField(max_length=45)
    logo_url           = models.URLField(max_length=2000, default='')

    class Meta:
        db_table = "taxi_companies"

class TaxiDriver(models.Model):
    name               = models.CharField(max_length=45)
    taxi_company       = models.ForeignKey("TaxiCompany", on_delete=models.CASCADE)
    profile_url        = models.URLField(max_length=2000, default='')
    introduction       = models.CharField(max_length=2000)

    class Meta:
        db_table = "taxi_drivers"

class DriverReview(models.Model):
    taxi_driver       = models.ForeignKey("TaxiDriver", on_delete=models.CASCADE)
    user              = models.ForeignKey("users.User", on_delete=models.CASCADE)
    rating            = models.IntegerField()
    review            = models.CharField(max_length=2000)

    class Meta:
        db_table = "driver_reviews"
