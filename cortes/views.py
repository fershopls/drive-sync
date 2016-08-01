import os
import csv
import re
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils import timezone
from . import models

if False:
    models.Concept.objects.create(name='Desayuno')
    models.Concept.objects.create(name='Comida')
    models.Concept.objects.create(name='Kayak')
    models.Concept.objects.create(name='Bicicleta')
    models.Concept.objects.create(name='Velero')
    models.Concept.objects.create(name='Masaje')
    models.Concept.objects.create(name='Otro')
    
    models.Currency.objects.create(slug='mxn')
    models.Currency.objects.create(slug='usd')
    models.Currency.objects.create(slug='tpv')

# Create your views here.

def home (request):
    return render(request, 'home.html', {})

# Get Week by Date
# datetime.date(2010, 6, 16).strftime("%V")
# Get Date by Week
# datetime.strptime('2016:30-0', "%Y:%W-%w")
def week_view (request, week_id=None):
    week_begin = datetime.strptime(timezone.now().strftime("%Y")+':'+week_id+'-0', "%Y:%W-%w")
    week_end = datetime.strptime(timezone.now().strftime("%Y")+':'+str(int(week_id)+1)+'-0', "%Y:%W-%w")-timedelta(days=1)
    week_begin = week_begin.strftime("%Y-%m-%d")
    week_end = week_end.strftime("%Y-%m-%d")
    
    week_bookings = models.Booking.objects.filter(departure__range=[week_begin, week_end])
    
    return render(request, 'week_view.html', {'week_id': week_id, 'week_bookings': week_bookings})

import_path = '%s/static/upload.csv' % os.path.dirname(os.path.abspath(__file__))
def import_process (request):
    if not os.path.isfile(import_path):
        return HttpResponse("No File")
    
    with open(import_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        num_format = re.compile("^[\-]?[1-9][0-9]*\.?[0-9]+$")
        bookings_sync = []
        # Each line as array
        for row in reader:
            # Row[0] is BookingId
            if len(row) >= 9 and re.match(num_format, row[0]):
                booking = {
                    'book_nr': row[0],
                    'book_date': row[1],
                    'booker_name': row[2],
                    'guest_names': row[3],
                    'arrival': row[4],
                    'departure': row[5],
                    'status': row[6],
                    'total': row[7],
                    'commission': row[8],
                }
                booking['arrival'] = datetime.strptime(booking['arrival'], "%Y-%m-%d")
                booking['departure'] = datetime.strptime(booking['departure'], "%Y-%m-%d")
                booking['book_date'] = datetime.strptime(booking['book_date'], "%Y-%m-%d %H:%M")
                booking['total'] = int(booking['total'].replace("USD ", ''))
                booking['commission'] = float(booking['commission'].replace("USD ", ''))
                
                row = models.Booking.objects.filter(book_nr=booking['book_nr']).first()
                if row:
                    row.book_date = booking['book_date']
                    row.booker_name = booking['booker_name']
                    row.guest_names = booking['guest_names']
                    row.arrival = booking['arrival']
                    row.departure = booking['departure']
                    row.status = booking['status']
                    row.total = booking['total']
                    row.commission = booking['commission']
                    row.save()
                else:
                    row = models.Booking.objects.create(
                        book_nr=booking['book_nr'],
                        book_date=booking['book_date'],
                        booker_name=booking['booker_name'],
                        guest_names=booking['guest_names'],
                        arrival=booking['arrival'],
                        departure=booking['departure'],
                        status=booking['status'],
                        total=booking['total'],
                        commission=booking['commission'],
                    )
                bookings_sync.append(row)
                
        return redirect("%s?bookings_sync=%s" % (reverse('import_success'), len(bookings_sync)))

def import_view (request):
    if request.method == "POST":
        file_content = request.POST.get("content")
        with open(import_path, 'w') as file_:
            file_.write(file_content.encode('utf8'))
        if os.path.isfile(import_path):
            return redirect(reverse('import_process'))
        else:
            return redirect(reverse('import_error'))
    return render(request, 'import_view.html', {})

def import_success (request):
    return render(request, 'import_view.html', {'success':True, 'bookings_sync':request.GET.get('bookings_sync')})

def import_error (request):
    return render(request, 'import_view.html', {'success':False})

def booking_view (request, book_nr=None):
    booking = models.Booking.objects.filter(book_nr=book_nr).first()
    if not booking:
        return redirect(reverse('index'))
    
    return render(request, 'booking_view.html', {'booking':booking})