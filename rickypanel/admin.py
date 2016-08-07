from django.contrib import admin
from .models import Project, Event

class ProjectAdmin(admin.ModelAdmin):
	list_display = ["name", "api_key", "api_secret", "report_id"]
	class Meta:
		model = Project

class EventAdmin(admin.ModelAdmin):
	list_display = ["name", "timestamp", "token"]
	class Meta:
		model = Event

admin.site.register(Project, ProjectAdmin)
admin.site.register(Event, EventAdmin)
# Register your models here.
