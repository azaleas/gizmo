from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country_code = models.IntegerField()
    phone_number = models.BigIntegerField(unique=True)
    authy_id = models.IntegerField()
    
    def __str__(self):
        return self.user.username
