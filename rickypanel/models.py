from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
	users = models.ManyToManyField(User)
	name = models.CharField(max_length=100)
	api_key = models.CharField(max_length=100, unique=True)
	api_secret = models.CharField(max_length=100, unique=True)
	token = models.CharField(max_length=100, unique=True)
	report_id = models.IntegerField()
	def __unicode__(self):
		return self.name

class Event(models.Model):
	timestamp = models.IntegerField()
	name = models.CharField(max_length=100)
	token = models.CharField(max_length=100)
	date = models.CharField(max_length=100)
	os = models.CharField(max_length=100)
	prop1 = models.CharField(max_length=100)
	prop2 = models.CharField(max_length=100)
	prop3 = models.CharField(max_length=100)
# Create your models here.
