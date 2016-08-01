from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.home, name='index'),
    url(r'^week/(?P<week_id>[0-9]+)$', views.week_view, name='week_view'),
    url(r'^booking/(?P<book_nr>[0-9]+)$', views.booking_view, name='booking_view'),
    url(r'^import$', views.import_view, name='import_view'),
    url(r'^import/process$', views.import_process, name='import_process'),
    url(r'^import/success$', views.import_success, name='import_success'),
    url(r'^import/error$', views.import_error, name='import_error'),
]
