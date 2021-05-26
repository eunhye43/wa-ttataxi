from django.db        import models

class User(models.Model):
    name                 = models.CharField(max_length=45, null=True)
    profile_url          = models.URLField(max_length=2000, default='', null=True)
    password             = models.CharField(max_length=1000, null=True)
    phone_number         = models.CharField(max_length=100, null=True)
    marketing_agree      = models.IntegerField(null=True)
    refund_account       = models.CharField(max_length=1000, null=True)
    kakao_account        = models.CharField(max_length=1000, null=True)
    point                = models.IntegerField(default=0, null=True)
    kakao                = models.IntegerField(null=True)
    kakao_email          = models.CharField(max_length=1000, null=True)
    kakao_nickname       = models.CharField(max_length=200, null=True)
    coupon               = models.ManyToManyField("Coupon", through="UserCoupon", null=True)
    class Meta:
        db_table = "users"

class UserCoupon(models.Model):
    user                 = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon               = models.ForeignKey("Coupon", on_delete=models.CASCADE)

    class Meta:
        db_table = "user_coupons"

class Coupon(models.Model):
    name                 = models.CharField(max_length=45)
    image_url            = models.URLField(max_length=2000, default='')

    class Meta:
        db_table = "coupons"