"""mypanel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rickypanel.views import track_event, segmentation, home, make_user, dashboard, top_events

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^create_user/', make_user, name='make_user'),
    url(r'^admin/', admin.site.urls),
    url(r'^dashboard/', dashboard, name='dashboard'),
    url(r'^track/', track_event, name="track_event"),
    url(r'^segmentation/', segmentation, name="segmentation"),
    url(r'^events/', top_events, name="top_events")
]

#dashboard/(?P<username>.*)$