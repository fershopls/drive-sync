from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.home, name='index'),
    url(r'^config$', views.config_view, name='config_view'),
    
    url(r'^week/(?P<week_id>[0-9]+)$', views.week_view, name='week_view'),
    url(r'^week/export$', views.week_export, name='week_export'),
    
    url(r'^booking/(?P<book_nr>[0-9]+)$', views.booking_view, name='booking_view'),
    url(r'^booking/(?P<book_nr>[0-9]+)/payment$', views.do_booking_payment, name='do_booking_payment'),
    url(r'^booking/(?P<book_nr>[0-9]+)/service$', views.do_booking_service, name='do_booking_service'),
    url(r'^import$', views.import_view, name='import_view'),
    url(r'^import/process$', views.import_process, name='import_process'),
    url(r'^import/success$', views.import_success, name='import_success'),
    url(r'^import/error$', views.import_error, name='import_error'),
    
    url(r'^accounts/login', views.accounts_login, name='accounts_login')
]
