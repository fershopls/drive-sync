#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import httplib2
from oauth2client import client
from apiclient.discovery import build
from oauth2client.contrib.django_util.storage import DjangoORMStorage as Storage
from casalamat import settings

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

def accounts_login (request):
    return redirect('/admin')

@login_required
def home (request):
    return redirect(reverse('week_view', kwargs={'week_id':datetime.now().strftime('%U')}))


flow = client.flow_from_clientsecrets(settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
                                  scope='https://www.googleapis.com/auth/drive', 
                                  redirect_uri='http://localhost:8000/config/access')

@login_required
def config_view (request):
    storage = Storage(models.CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        drive_uri = flow.step1_get_authorize_url()
        return render(request, 'config.html', {'oauth_drive_uri':drive_uri})
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build("drive", "v3", http=http)
        
        results = service.files().list(
            pageSize=10,fields="nextPageToken, files(id, name)").execute()
        
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))
        
        return JsonResponse(items)


@login_required
def config_access (request):
    credential = flow.step2_exchange(request.REQUEST.get('code'))
    storage = Storage(models.CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)
    return HttpResponseRedirect("/config")




    

# Get Week by Date
# datetime.date(2010, 6, 16).strftime("%V")
# Get Date by Week
# datetime.strptime('2016:30-0', "%Y:%W-%w")
# https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
# %U vs %W vs %V
@login_required
def week_view (request, week_id=None):
    week_begin = datetime.strptime(timezone.now().strftime("%Y")+':'+week_id+'-0', "%Y:%U-%w")
    week_end = datetime.strptime(timezone.now().strftime("%Y")+':'+str(int(week_id)+1)+'-0', "%Y:%U-%w")-timedelta(days=1)
    week_begin = week_begin.strftime("%Y-%m-%d")
    week_end = week_end.strftime("%Y-%m-%d")
    
    week_bookings = models.Booking.objects.filter(departure__range=[week_begin, week_end])
    
    return render(request, 'week_view.html', {'week_id': week_id, 'week_bookings': week_bookings})

@login_required
def week_export (request):
    week_id = request.POST.get('week_id')
    usd_value = float(request.POST.get('usd_value'))
    
    week_begin = datetime.strptime(timezone.now().strftime("%Y")+':'+week_id+'-0', "%Y:%U-%w")
    week_end = datetime.strptime(timezone.now().strftime("%Y")+':'+str(int(week_id)+1)+'-0', "%Y:%U-%w")-timedelta(days=1)
    week_begin = week_begin.strftime("%Y-%m-%d")
    week_end = week_end.strftime("%Y-%m-%d")
    week_bookings = models.Booking.objects.filter(departure__range=[week_begin, week_end])
    
    # Create the HttpResponse object with the appropriate CSV header.
    #response = HttpResponse(content_type='text/plain')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="W%s_%s.csv"' % (week_id,week_end)

    concepts = models.Concept.objects.all()
    currencies = models.Currency.objects.all()
    writer = csv.writer(response)
    writer.writerow([])
    writer.writerow(["","WEEK NUMBER",week_id])
    writer.writerow(["","USD VALUE",usd_value])
    writer.writerow([])
    headers = ["Book_nr","Book_date","Booker_name","Guest_names","Arrival","Departure","Status","Total","Commission","Subtotal",
               "","Folio Registro"]
    for concept in concepts:
        headers.append(concept.name)
    
    headers = headers + ["Subtotal",""]
    
    for currency in currencies:
        headers.append(currency.slug.upper())
    
    headers = headers + ["Gran Total", "Por Recibir","","Notas"]
    
    writer.writerow(headers)
    for b in week_bookings:
        total_mxn = b.total*usd_value
        row = [
            b.book_nr,
            b.book_date,
            b.booker_name.encode('utf8'),
            b.guest_names.encode('utf8'),
            b.arrival,
            b.departure,
            b.status.encode('utf8'),
            b.total,
            b.commission,
            total_mxn,
            "",
            b.folio
        ]
        concept_total = 0
        for concept in concepts:
            service = b.service_set.filter(concept__id=concept.id).first()
            if service:
                row.append(service.value)
                concept_total += service.value
            else:
                row.append("0")
        row =  row + [concept_total, ""]
        
        payment_total = 0
        for currency in currencies:
            payment = b.payment_set.filter(currency__id=currency.id).first()
            if payment:
                row.append(payment.value)
                payment_total += payment.value if payment.currency.slug != 'usd' else payment.value*usd_value
            else:
                row.append("0")
        
        grand_total = total_mxn+concept_total
        row.append(grand_total)
        row.append(grand_total - payment_total)
        row.append(b.notes)
        
        writer.writerow(row)
    

    return response



import_path = '%s/static/upload.csv' % os.path.dirname(os.path.abspath(__file__))
@login_required
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

@login_required
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

@login_required
def import_success (request):
    return render(request, 'import_view.html', {'success':True, 'bookings_sync':request.GET.get('bookings_sync')})

@login_required
def import_error (request):
    return render(request, 'import_view.html', {'success':False})

@login_required
def booking_view (request, book_nr=None):
    booking = models.Booking.objects.filter(book_nr=book_nr).first()
    if not booking:
        return redirect(reverse('index'))
    currencies = models.Currency.objects.all()
    concepts = models.Concept.objects.all()
    
    return render(request, 'booking_view.html', {'booking':booking, 'currencies': currencies, 'concepts':concepts})

@login_required
def do_booking_payment (request, book_nr=None):
    booking = models.Booking.objects.filter(book_nr=book_nr).first()
    if not booking or request.method != "POST" or not request.POST.get('payment_value'):
        return redirect(reverse('booking_view', kwargs={'book_nr':book_nr}))
    
    payment_value = int(request.POST.get('payment_value'))
    payment_currency = request.POST.get('payment_currency')
    
    
    booking_payment = booking.payment_set.filter(currency__slug=payment_currency).first()
    
    if booking_payment:
        booking_payment.value = payment_value
        booking_payment.save()
    else:
        currency = models.Currency.objects.filter(slug=payment_currency).first()
        if not currency:
            return redirect(reverse('index'))
        
        booking.payment_set.create(value=payment_value, currency=currency)
    return redirect(reverse('booking_view', kwargs={'book_nr':book_nr}))

@login_required
def do_booking_service (request, book_nr=None):
    booking = models.Booking.objects.filter(book_nr=book_nr).first()
    if not booking or request.method != "POST" or not request.POST.get('value'):
        return redirect(reverse('booking_view', kwargs={'book_nr':book_nr}))
    
    value = int(request.POST.get('value'))
    concept_id = int(request.POST.get('concept_id'))
    
    
    booking_service = booking.service_set.filter(concept__id=concept_id).first()
    
    if booking_service:
        booking_service.value = payment_value
        booking_service.save()
    else:
        concept = models.Concept.objects.filter(id=concept_id).first()
        if not concept:
            return redirect(reverse('index'))
        
        booking.service_set.create(value=value, concept=concept)
    return redirect(reverse('booking_view', kwargs={'book_nr':book_nr}))
    
    