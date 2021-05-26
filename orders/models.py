from django.db import models

class Order(models.Model):
    user                 = models.ForeignKey("users.User", on_delete=models.CASCADE)
    status               = models.ForeignKey("Status", on_delete=models.CASCADE)
    created_at           = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = "orders"

class Status(models.Model):
    name                 = models.CharField(max_length=45)

    class Meta:
        db_table = "status"

class ScheduleOrder(models.Model):
    schedule             = models.ForeignKey("taxis.Schedule", on_delete=models.CASCADE)
    order                = models.ForeignKey("Order", on_delete=models.CASCADE)
    passenger_number     = models.IntegerField()
    tax                  = models.IntegerField()
    
    class Meta:
        db_table = "schedule_orders"

class Passenger(models.Model):
    last_name             = models.CharField(max_length=200)
    first_name            = models.CharField(max_length=200)
    gender                = models.CharField(max_length=45)
    nationality           = models.CharField(max_length=45)
    birth_date            = models.DateTimeField()
    order                 = models.ForeignKey("Order", on_delete=models.CASCADE)
    
    class Meta:
        db_table = "passengers"