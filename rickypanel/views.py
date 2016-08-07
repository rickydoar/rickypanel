from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Project, Event
import time, datetime, json, hashlib
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world")

def track_event(request):
	token = request.GET.get("token")
	name = request.GET.get("name")
	os = request.GET.get("os", "Undefined")
	distinct_id = request.GET.get("distinct_id")
	prop1 = request.GET.get("prop1", "Undefined")
	prop2 = request.GET.get("prop2", "Undefined")
	prop3 = request.GET.get("prop3", "Undefined")
	timestamp = float(request.GET.get("time"))
	if not timestamp:
		timestamp = int(time.time())
	try:
		date = (datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'))
	except:
		return HttpResponse(json.dumps({"success":0, "error":"invalid time value"}))
	if token and name:
		event = Event.objects.create(token=token, name=name, timestamp=timestamp, date=date, os=os,
			prop1=prop1, prop2=prop2, prop3=prop3)
		return HttpResponse("1")
	else:
		return HttpResponse("0")

#built to only support daily, currently not scalable to other units
def segmentation(request):
	sig = request.GET.get("sig")
	api_key = request.GET.get("api_key")
	to_date = request.GET.get("to_date")
	from_date = request.GET.get("from_date")
	event = request.GET.get("event")
	on = request.GET.get("on")
	expire = request.GET.get("expire")
	params = request.GET.dict()
	del params['sig']
	try:
		api_secret = Project.objects.get(api_key=api_key).api_secret
	except:
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid api key"}))
	try:
		expire = int(expire)
	except:
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid expire parameter"}))
	if expire < time.time():
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid expire parameter"}))
	secure_sig = generate_sig(params, api_secret)
	print secure_sig
	if secure_sig == sig:
		try:
			to_date_object = datetime.date(int(to_date[0:4]), int(to_date[5:7]), int(to_date[8:10]))
			from_date_object = datetime.date(int(from_date[0:4]), int(from_date[5:7]), int(from_date[8:10]))
		except:
			return HttpResponse(json.dumps({"request":request.GET, "error":"ISO date format required"}))
		delta = to_date_object - from_date_object
		result = {}
		segments = set()
		for i in range(delta.days + 1):
			current_day = str(from_date_object + datetime.timedelta(days=i))
			events = Event.objects.filter(name=event).filter(date=current_day)
			if on:
				result[current_day] = {}
				for item in events:
					segment = getattr(item, on)
					segments.add(segment)
					if result[current_day].get(segment):
						result[current_day][segment]+= 1
					else:
						result[current_day][segment] = 1
			else:
				result[current_day] = len(events)
		if on:
			for day in result:
				for segment in segments:
					if segment not in result[day].keys():
						result[day][segment] = 0
		return HttpResponse(json.dumps(result))
	else:
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid api signature"}))

def generate_sig(params, api_secret):
	keys = sorted(params.keys())
	args_joined = ''
	for arg in keys:
		args_joined += arg + '=' + params[arg]
	args_joined += api_secret
	hash = hashlib.md5(args_joined)
	return hash.hexdigest()