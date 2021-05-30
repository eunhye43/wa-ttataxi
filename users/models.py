from django.db        import models

class User(models.Model):
    name                 = models.CharField(max_length=45)
    email                = models.CharField(max_length=1000)
    password             = models.CharField(max_length=1000)
    kakao_id             = models.IntegerField(null=True)
    phone_number         = models.CharField(max_length=100, null=True)
    profile_url          = models.URLField(max_length=2000, null=True)
    refund_account       = models.CharField(max_length=1000, null=True)
    marketing_agreement  = models.IntegerField(null=True)
    point                = models.IntegerField(default=0)
    coupon               = models.ManyToManyField("Coupon", through="UserCoupon", null=True)
    refresh_token        = models.CharField(max_length=1000, null=True)
    class Meta:
        db_table = "users"

class KakaoToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=2000)
    class Meta:
        db_table = "kakao_tokens"

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
