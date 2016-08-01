from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Booking)
admin.site.register(models.Concept)
admin.site.register(models.Service)
admin.site.register(models.Currency)
admin.site.register(models.Payment)