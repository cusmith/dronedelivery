from django.db import models

# Create your models here.
class User(models.Model):
	name = models.CharField(max_length=50)
	username = models.CharField(max_length=50)
	address = models.CharField(max_length=100)
	email = models.CharField(max_length=50)
	phone_number = model.CharField(max_length=10)