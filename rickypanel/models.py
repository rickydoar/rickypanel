from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=100)
	api_key = models.CharField(max_length=100)
	api_secret = models.CharField(max_length=100)
	token = models.CharField(max_length=100)
	report_id = models.AutoField(primary_key=True)
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