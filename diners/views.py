
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import json,pytz
from time import sleep
import  pytz, json
from datetime import date, datetime, timedelta, time
from django.conf import settings

from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from diners.models import AccessLog
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Max, Min

from .models import AccessLog, Diner
from cloudkitchen.settings.base import PAGE_TITLE


def naive_to_datetime(nd):
    if type(nd) == datetime:
        if nd.tzinfo is not None and nd.tzinfo.utcoffset(nd) is not None: # Is Aware
            return nd
        else: # Is Naive
            return pytz.timezone('America/Mexico_City').localize(nd)              

    elif type(nd) == date:
        d = nd
        t = time(0,0)
        new_date = datetime.combine(d, t)
        return pytz.timezone('America/Mexico_City').localize(new_date)


def get_diners(initial_date, final_date):
    diners_logs_list = []

    diners_logs_objects = get_access_logs(initial_date, final_date)

    for diner_log in diners_logs_objects:
        diner_log_object = {
            'rfid': diner_log.RFID,
            'access': datetime.strftime(diner_log.access_to_room, "%B %d, %I, %H:%M:%S %p"),
            'number_day': get_number_day(diner_log.access_to_room),
        }
        if diner_log.diner:
            diner_log_object['SAP'] = diner_log.diner.employee_number
            diner_log_object['name'] = diner_log.diner.name
        else:
            diner_log_object['SAP'] = ''
            diner_log_object['name'] = ''
        diners_logs_list.append(diner_log_object)
    return diners_logs_list


def get_name_day(datetime_now):
    days_list = {
        'MONDAY': 'Lunes',
        'TUESDAY': 'Martes',
        'WEDNESDAY': 'Miércoles',
        'THURSDAY': 'Jueves',
        'FRIDAY': 'Viernes',
        'SATURDAY': 'Sábado',
        'SUNDAY': 'Domingo'
    }
    name_day = date(datetime_now.year, datetime_now.month, datetime_now.day)
    return days_list[name_day.strftime('%A').upper()]


def get_number_day(dt):
    days = {
        'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sábado': 5, 'Domingo': 6,
    }
    return days[get_name_day(dt)]


def start_datetime(back_days):
    start_date = date.today() - timedelta(days=back_days) 
    return naive_to_datetime(start_date)


def end_datetime(back_days):
    end_date = start_datetime(back_days) + timedelta(days=1)
    return naive_to_datetime(end_date)


def naive_to_datetime(nd):
    if type(nd) == datetime:
        if nd.tzinfo is not None and nd.tzinfo.utcoffset(nd) is not None: # Is Aware
            return nd
        else: # Is Naive
            return pytz.timezone('America/Mexico_City').localize(nd)              

    elif type(nd) == date:
        d = nd
        t = time(0,0)
        new_date = datetime.combine(d, t)
        return pytz.timezone('America/Mexico_City').localize(new_date)


def diners_paginator(request, queryset, num_pages):
    result_list = Paginator(queryset, num_pages)

    try:
        num_page = int(request.GET['num_page'])
    except:
        num_page = 1

    if num_page <= 0:
        num_page = 1

    if num_page > result_list.num_pages:
        num_page = result_list.num_pages
    
    if result_list.num_pages >= num_page:
        page = result_list.page(num_page)
    
        context = {
            'queryset': page.object_list,
            'num_page': num_page,
            'pages': result_list.num_pages,
            'has_next': page.has_next(),
            'has_prev': page.has_previous(),
            'next_page': num_page + 1,
            'prev_page': num_page - 1,
            'first_page': 1,
        }
    return context


def parse_to_datetime(dt):
    day = int(dt.split('-')[0])
    month = int(dt.split('-')[1])
    year = int(dt.split('-')[2])
    parse_date = date(year, month, day)
    return  naive_to_datetime(parse_date)


def get_access_logs(dt):
    initial_date = naive_to_datetime(dt)
    final_date = naive_to_datetime(initial_date + timedelta(days=1))
    return AccessLog.objects.filter(access_to_room__range=(initial_date, final_date)).order_by('-access_to_room')


def get_access_logs(initial_date, final_date):
    return AccessLog.objects.filter(access_to_room__range=(initial_date, final_date)).order_by('-access_to_room')


def get_access_logs_today():
    year = int(datetime.now().year)
    month = int(datetime.now().month)
    day = int(datetime.now().day)
    initial_date = naive_to_datetime(date(year, month, day))
    final_date = naive_to_datetime(initial_date + timedelta(days=1))
    return AccessLog.objects.filter(access_to_room__range=(initial_date, final_date)).order_by('-access_to_room')


def get_all_access_logs():
    return AccessLog.objects.all().order_by('-access_to_room')


def get_start_week_day(day):
    format = "%w"
    number_day = int(naive_to_datetime(day).strftime(format))
    if number_day ==  0:
        number_day = 7
    else:
        day = naive_to_datetime(day) - timedelta(days=number_day-1)


def get_diners_per_hour():
    hours_list = []
    hours_to_count = 12
    start_hour = 5
    customter_count = 0    
    logs = get_access_logs_today()

    while start_hour <= hours_to_count:

        hour = {            
            'count': None,
        }

        for log in logs:
            datetime = str(log.access_to_room)
            date,time = datetime.split(" ")    
            if(time.startswith("0"+str(start_hour))):
                customter_count += 1 
            hour['count'] = customter_count

        hours_list.append(hour)        
        customter_count = 0
        start_hour += 1
        total_entries = 0

    return json.dumps(hours_list) 
   

def get_diners_actual_week():
    week_diners_list = []
    total_entries = 0
    days_to_count = get_number_day(date.today())
    day_limit = days_to_count
    start_date_number = 0
    
    while start_date_number <= day_limit:
        day_object = {
            'date': str(start_datetime(days_to_count).date().strftime('%d-%m-%Y')),
            'day_name': None,
            'entries': None,
            'number_day': get_number_day(start_datetime(days_to_count).date())
        }
        
        logs = AccessLog.objects.filter(access_to_room__range=[start_datetime(days_to_count), end_datetime(days_to_count)])

        for log in logs:                
            total_entries += 1;

        day_object['entries'] = str(total_entries)
        day_object['day_name'] = get_name_day(start_datetime(days_to_count).date())

        week_diners_list.append(day_object)

        # restarting counters
        days_to_count -= 1
        total_entries = 0
        start_date_number += 1

    return json.dumps(week_diners_list)



# ------------------------- Django Views ----------------------------- #

@csrf_exempt
def RFID(request):
    if request.method == 'POST':
        rfid = str(request.body).split('"')[3].replace(" ", "")
        if settings.DEBUG:
            print(rfid)

        if rfid is None:
            if settings.DEBUG:
                print('no se recibio rfid')
            return HttpResponse('No se recibió RFID\n')
        else:
            access_logs = get_access_logs_today()
            exists = False
            
            for log in access_logs:
                if rfid == log.RFID:
                    exists = True
                    break

            if exists:
                if settings.DEBUG:
                    print('El usuario ya se ha registrado')
                return HttpResponse('El usuario ya se ha registrado')
            else:
                if len(rfid) < 7:
                    try:
                        diner = Diner.objects.get(RFID=rfid)
                        new_access_log = AccessLog(diner=diner, RFID=rfid)
                        new_access_log.save()
                    except Diner.DoesNotExist:
                        new_access_log = AccessLog(diner=None, RFID=rfid)
                        new_access_log.save()   
                else:
                    if settings.DEBUG:
                        print('RFID Inválido\n')
                    return HttpResponse('RFID Inválido\n')

        return HttpResponse('Operacion Terminada\n')

    else:
        return redirect('diners:diners')

def diners(request):
    count = 0
    diners_list = []    
    total_diners = len(diners_list)
    diners_objects = get_access_logs_today()
    total_diners = diners_objects.count()
    pag = diners_paginator(request, diners_objects, 50)
    template = 'diners.html'
    title = 'Comensales del Dia'
    page_title = PAGE_TITLE

    context={
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'diners' : pag['queryset'],                
        'paginator': pag,
        'total_diners': total_diners,
    }
    return render(request, template, context)

def diners_logs(request):
    all_entries = AccessLog.objects.all()
    diners = Diner.objects.all()

    def get_entries(initial_date, final_date):
        """
        Gets the following properties for each week's day: Name, Date and Earnings
        """
        limit_day = initial_date + timedelta(days=1)
        week_diners_list = []
        count = 1
        total_entries = 0
        total_days = (final_date - initial_date).days

        while count <= total_days:
            diners = all_entries.filter(access_to_room__range=[initial_date, limit_day])
            day_object = {
                'date': str(initial_date.date().strftime('%d-%m-%Y')),
                'day_name': None,
                'entries': None,
                'number_day': get_number_day(initial_date),
            }

            day_object['day_name'] = get_name_day(initial_date.date())
            day_object['entries'] = diners.count()

            week_diners_list.append(day_object)

            # Reset datas
            limit_day += timedelta(days=1)
            initial_date += timedelta(days=1)
            total_entries = 0
            count += 1

        return week_diners_list

    if request.method == 'POST':
        if request.POST['type'] == 'diners_logs_week':
            dt_year = request.POST['dt_year']
            initial_date = request.POST['dt_week'].split(',')[0]
            final_date = request.POST['dt_week'].split(',')[1]
            initial_date = parse_to_datetime(initial_date)
            final_date = parse_to_datetime(final_date) + timedelta(days=1)

            diners_logs = get_diners(initial_date, final_date)
            entries = get_entries(initial_date, final_date)
            data = {
                'diners': diners_logs,
                'entries': entries,
            }
            return JsonResponse(data)

        elif request.POST['type'] == 'diners_logs_day':
            """
            Returns a list with objects:
            Each object has the following characteristics
            """
            access_logs_day_list = []
            start_date = naive_to_datetime(datetime.strptime(request.POST['date'], '%d-%m-%Y').date())
            end_date = naive_to_datetime(start_date + timedelta(days=1))
            access_logs = all_entries.filter(access_to_room__range=[start_date, end_date])

            for access_log in access_logs:
                """
                Filling in the sales list of the day
                """
                earnings_sale_object = {
                    'access_id': access_log.id,
                    'datetime': timezone.localtime(access_log.access_to_room),
                    'number_day': get_number_day(start_date), 
                }
                
                access_logs_day_list.append(earnings_sale_object)
            return JsonResponse({'access_logs_day_list': access_logs_day_list})

        if request.POST['type'] == 'diners_logs':
            diners_objects_list = []

            for entry in all_entries:
                diner_object = {
                    'id': entry.id,
                    'Nombre': '',
                    'RFID': entry.RFID,
                    'SAP': '',
                    'Fecha de Acceso': (entry.access_to_room - timedelta(hours=5)).date(),
                    'Hora de Acceso': (entry.access_to_room - timedelta(hours=5)).time(),
                }
                for diner in diners:
                    if entry.RFID == diner.RFID:
                        diner_object['SAP'] = diner.employee_number
                        diner_object['Nombre'] = diner.name

                diners_objects_list.append(diner_object)

            return JsonResponse({'diner_logs': diners_objects_list})
            
    else:
        all_diners_objects = get_all_access_logs()
        today_diners_objects = get_access_logs_today()
        total_diners = all_diners_objects.count()
        total_diners_today = today_diners_objects.count()

        def get_dates_range():
            """
            Returns a JSON with a years list.
            The years list contains years objects that contains a weeks list
                and the Weeks list contains a weeks objects with two attributes: 
                start date and final date. Ranges of each week.
            """
            try:
                min_year = all_diners_objects.aggregate(Min('access_to_room'))['access_to_room__min'].year
                max_year = all_diners_objects.aggregate(Max('access_to_room'))['access_to_room__max'].year
                years_list = [] # [2015:object, 2016:object, 2017:object, ...]
            except Exception as e:
                if settings.DEBUG:
                    print('Error:' , e)
                return HttpResponse('No hay registros')
                
            while max_year >= min_year:
                year_object = { # 2015:object or 2016:object or 2017:object ...
                    'year' : max_year,
                    'weeks_list' : []
                }

                diners_per_year = all_diners_objects.filter(
                    access_to_room__range=[naive_to_datetime(date(max_year,1,1)),naive_to_datetime(date(max_year,12,31))])
                
                for diner in diners_per_year:
                    if len(year_object['weeks_list']) == 0: 
                        """
                        Creates a new week_object in the weeks_list of the actual year_object
                        """
                        start_week_day = get_start_week_day(diner.access_to_room.date())
                        week_object = { 
                            'week_number': diner.access_to_room.isocalendar()[1],
                            'start_date': diner.access_to_room.date().strftime("%d-%m-%Y"),
                            'end_date': diner.access_to_room.date().strftime("%d-%m-%Y"),
                        }
                        year_object['weeks_list'].append(week_object)

                        # End if
                    else: 
                        """
                        Validates if exists some week with an indentical week_number of the actual year
                        If exists a same week in the list validates the start_date and the end_date,
                        In each case valid if there is an older start date or a more current end date 
                            if it is the case, update the values.
                        Else creates a new week_object with the required week number
                        """
                        existing_week = False
                        for week_object in year_object['weeks_list']:
                            if week_object['week_number'] == diner.access_to_room.isocalendar()[1]:
                                # There's a same week number
                                existing_week = True
                                if datetime.strptime(week_object['start_date'], "%d-%m-%Y").date() > diner.access_to_room.date():
                                    exists = True
                                    week_object['start_date'] = diner.access_to_room.date().strftime("%d-%m-%Y")
                                elif datetime.strptime(week_object['end_date'], "%d-%m-%Y").date() < diner.access_to_room.date():
                                    week_object['end_date'] = diner.access_to_room.date().strftime("%d-%m-%Y")
                                existing_week = True
                                break

                        if not existing_week:
                            # There's a different week number
                            week_object = { 
                                'week_number': diner.access_to_room.isocalendar()[1],
                                'start_date': diner.access_to_room.date().strftime("%d-%m-%Y"),
                                'end_date': diner.access_to_room.date().strftime("%d-%m-%Y"),
                            }
                            year_object['weeks_list'].append(week_object)

                        #End else
                years_list.append(year_object)
                max_year -= 1
            # End while
            return json.dumps(years_list)

        pag = diners_paginator(request, all_diners_objects, 50)
        template = 'diners_logs.html'
        title = 'Registro de comensales'
        page_title = PAGE_TITLE

        context={
            'title': PAGE_TITLE + ' | ' + title,
            'page_title': title,
            'diners': pag['queryset'],
            'paginator': pag,
            'total_diners': total_diners,
            'total_diners_today': total_diners_today,
            'diners_hour': get_diners_per_hour(),
            'diners_week': get_diners_actual_week(),
            'dates_range': get_dates_range(),
        }
        return render(request, template, context)    


# --------------------------- TEST ------------------------

def test(request):
    rfids = [ 52661 ,]



    for rfid in rfids:
        dt = naive_to_datetime(datetime(2017,3,23,13,30))
        rfid = str(rfid)
        if rfid is None:
            print('No se recibió RFID\n')
        else:
            access_logs = get_access_logs(dt)
            exists = False
            
            for log in access_logs:
                if rfid == log.RFID:
                    exists = True
                    if settings.DEBUG:
                        print('es identico...........')
                    break

            if exists:
                if settings.DEBUG:
                    print('El usuario ya se ha registrado')
            else:
                if len(rfid) < 7:
                    try:
                        diner = Diner.objects.get(RFID=rfid)
                        new_access_log = AccessLog(diner=diner, RFID=rfid, access_to_room=dt)
                        new_access_log.save()
                    except Diner.DoesNotExist:
                        new_access_log = AccessLog(diner=None, RFID=rfid, access_to_room=dt)
                        new_access_log.save()
                        if settings.DEBUG:   
                            print('Nuevo comensal\n')
                else:
                    if settings.DEBUG:
                        print('RFID Inválido\n')

    return HttpResponse('Hola')