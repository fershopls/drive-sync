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
    
    internal_notes = models.TextField(blank=True)
    
    def __str__ (self):
        return "[%s] %s" % (self.book_nr, self.booker_name)
    
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
    folio = models.SmallIntegerField()
    concept = models.ForeignKey(Concept)
    currency = models.ForeignKey(Currency)
    value = models.SmallIntegerField()
    
    def __str__(self):
        return "%s %s $%s%s" % (self.booking, self.concept.name, self.value, self.currency.slug)
    
class Payment (models.Model):
    booking = models.ForeignKey(Booking)
    currency = models.ForeignKey(Currency)
    value = models.IntegerField()
    
    def __str__(self):
        return "%s $%s %s" % (self.booking, self.value, self.currency.slug)
