from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Project, Event
import time, datetime, json, hashlib, uuid
from django.http import HttpResponse

def home(request):
	if request.user.is_authenticated():
		return redirect('/dashboard/')
	context = {}
	template = "home.html"
	if request.POST:
		username = user_login(request)
		if username:
			return HttpResponseRedirect("/dashboard/")
		else:
			context["error"] = True
	return render(request, template, context)

def dashboard(request):
	if not request.user.is_authenticated():
		return redirect('/')
	else:
		context = {}
		if request.POST.get("project"):
			api_key = str(uuid.uuid4()).replace('-','')
			Project.objects.create(user=request.user, name=request.POST["project"], api_key=api_key,
				api_secret=str(uuid.uuid4()).replace('-',''), token=str(uuid.uuid4()).replace('-',''))
			return redirect('/')
		elif request.POST:
			user_logout(request)
			return redirect('/')
		user = User.objects.get(username=request.user)
		email = user.email
		all_projects = user.project_set.all()
		if len(all_projects) == 0:
			api_key = str(uuid.uuid4()).replace('-','')
			Project.objects.create(user=request.user, name="New project", api_key=api_key,
				api_secret=str(uuid.uuid4()).replace('-',''), token=str(uuid.uuid4()).replace('-',''))
		 	return redirect('/')
		context.update({"username":request.user, "email":email, "all_projects":all_projects})
		template = "dashboard.html"
		return render(request, template, context)

def make_user(request):
	if request.user.is_authenticated():
		return redirect('/dashboard/')
	template = "create_user.html"
	if request.POST:
		email = request.POST['email']
		password = request.POST['password']
		try:
			User.objects.get(email=request.POST['email'])
		except:
			username = str(uuid.uuid4())[:11].replace('-','')
			new_user = User.objects.create_user(username, email, password)
			if user_login(request):
				return HttpResponseRedirect("/dashboard/")
	return render(request, template)

def user_logout(request):
	logout(request)
	return redirect('/')
	
def user_login(request):
	try:
		username = User.objects.get(email=request.POST['email']).username
		user = authenticate(username=username, password=request.POST['password'])
		if user is not None:
			# the password verified for the user
			if user.is_active:
				login(request, user)
				return username
			else:
				return False
		else:
		    # the authentication system was unable to verify the username and password
		    return False
	except:
		print("User does not exist")

def track_event(request):
	if len(request.GET) == 0:
		return HttpResponse(json.dumps({"success":0, "error":"no data"}))
	token = request.GET.get("token")
	name = request.GET.get("event")
	os = request.GET.get("os", "Undefined")
	distinct_id = request.GET.get("distinct_id")
	prop1 = request.GET.get("prop1", "Undefined")
	prop2 = request.GET.get("prop2", "Undefined")
	prop3 = request.GET.get("prop3", "Undefined")
	if request.GET.get("time"):
		timestamp = float(request.GET.get("time"))
	else:
		timestamp = int(time.time())
	try:
		date = (datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'))
	except:
		return HttpResponse(json.dumps({"success":0, "error":"invalid time value"}))
	if token and name:
		event = Event.objects.create(token=token, name=name, timestamp=timestamp, date=date, os=os,
			prop1=prop1, prop2=prop2, prop3=prop3)
		return HttpResponse(json.dumps({"success":1, "error":"none"}))
	else:
		return HttpResponse(json.dumps({"success":0, "error":"missing required parameters"}))

def top_events(request):
	sig = request.GET.get("sig")
	print request.GET.get("api_key")
	try:
		api_secret = Project.objects.get(api_key=request.GET.get("api_key")).api_secret
		token = Project.objects.get(api_key=request.GET.get("api_key")).token
	except:
		return HttpResponse(json.dumps({"request":request.GET, "error":"no project found"}))
	if not sig:
		return HttpResponse(json.dumps({"request":request.GET, "error":"no api signature"}))
	try:
		expire = request.GET.get("expire")
		expire = int(expire)
	except:
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid expire parameter"}))
	if expire < time.time():
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid expire parameter"}))
	secure_sig = generate_sig(request, api_secret)
	print secure_sig
	if secure_sig == sig:
		events = Event.objects.filter(token=token)
		event_counts = {}
		for event in events:
			if event_counts.get(event.name):
				event_counts[event.name] += 1
			else:
				event_counts[event.name] = 1
		return HttpResponse(json.dumps(event_counts))
	else:
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid api signature"}))


def segmentation(request):
	sig = request.GET.get("sig")
	to_date = request.GET.get("to_date")
	from_date = request.GET.get("from_date")
	name = request.GET.get("event")
	on = request.GET.get("on")
	expire = request.GET.get("expire")
	try:
		project = Project.objects.get(api_key=request.GET.get("api_key"))
		api_secret = project.api_secret
		token = project.token
	except:
		return HttpResponse(json.dumps({"request":request.GET, "error":"no project found"}))
	if not sig:
		return HttpResponse(json.dumps({"request":request.GET, "error":"no api signature"}))
	try:
		expire = int(expire)
	except:
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid expire parameter"}))
	if expire < time.time():
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid expire parameter"}))
	secure_sig = generate_sig(request, api_secret)
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
			events = Event.objects.filter(name=name).filter(date=current_day).filter(token=token)
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
				result[current_day] = {}
				result[current_day][name] = len(events)
		if on:
			for day in result:
				for segment in segments:
					if segment not in result[day].keys():
						result[day][segment] = 0
		return HttpResponse(json.dumps(result))
	else:
		return HttpResponse(json.dumps({"request":request.GET, "error":"invalid api signature"}))

def generate_sig(request, api_secret):
	request.GET.get("api_key")
	params = request.GET.dict()
	del params['sig']
	keys = sorted(params.keys())
	args_joined = ''
	for arg in keys:
		args_joined += arg + '=' + params[arg]
	args_joined += api_secret
	hash = hashlib.md5(args_joined)
	return hash.hexdigest()