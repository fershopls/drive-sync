from django.db import models

# Create your models here.
# Get Week by Date
# datetime.date(2010, 6, 16).strftime("%V")
# Get Date by Week
# datetime.strptime('2016:30-0', "%Y:%W-%w")
# Todo: Deactivate nullable fields

class Booking (models.Model):
    book_nr = models.IntegerField()
    book_date = models.DateTimeField()
    booker_name = models.CharField(max_length=200)
    guest_names = models.CharField(max_length=200)
    arrival = models.DateField()
    departure = models.DateField()
    status = models.CharField(max_length=200)
    total = models.SmallIntegerField()
    commission = models.FloatField(default=0)
    
    folio = models.SmallIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    def __unicode__ (self):
        return "%s %s" % (self.book_nr, self.booker_name)
    
    def get_payments (self):
        payments = []
        for currency in Currency.objects.all():
            p = self.payment_set.filter(currency__slug=currency.slug).first()
            if not p:
                p = {"currency":{"slug":currency.slug}, "value":0}
            payments.append(p)
        return payments
    
    def get_services (self):
        services = []
        for concept in Concept.objects.all():
            s = self.service_set.filter(concept__id=concept.id).first()
            if not s:
                s = {"concept":{"name":concept.name}, "value":0}
            services.append(s)
        return services
    
class Concept (models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class Currency (models.Model):
    slug = models.CharField(max_length=10)
    
    def __str__(self):
        return self.slug
    
class Service (models.Model):
    booking = models.ForeignKey(Booking)
    concept = models.ForeignKey(Concept)
    #currency = models.ForeignKey(Currency)
    value = models.SmallIntegerField()
    
    def __str__(self):
        return "%s %s $%s%s" % (self.booking, self.concept.name, self.value, self.currency.slug)
    
class Payment (models.Model):
    booking = models.ForeignKey(Booking)
    currency = models.ForeignKey(Currency)
    value = models.IntegerField()
    
    def __str__(self):
        return "%s $%s %s" % (self.booking, self.value, self.currency.slug)
    
class Export (models.Model):
    week_number = models.SmallIntegerField()
    file_id = models.CharField(max_length=200)
    file_path = models.CharField(max_length=200)
    usd_value = models.SmallIntegerField()
    export_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "W%s #%s" % (self.week_number, self.file_id)




