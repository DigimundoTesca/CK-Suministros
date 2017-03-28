
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import json,pytz
from time import sleep
import  pytz, json
from datetime import date, datetime, timedelta, time

from django.http import HttpResponse
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


def get_number_day():
    days = {
        'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sábado': 5, 'Domingo': 6,
    }
    return days[get_name_day(datetime.now())]

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


def get_access_log(dt):
    initial_date = naive_to_datetime(dt)
    final_date = naive_to_datetime(initial_date + timedelta(days=1))
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

# ------------------------- Django Views ----------------------------- #

@csrf_exempt
def RFID(request):
    if request.method == 'POST':
        rfid = str(request.body).split('"')[3].lstrip()
        if rfid is None:
            return HttpResponse('No se recibió RFID\n')
        else:
            access_logs = get_access_logs_today()
            exists = False
            
            for log in access_logs:
                if rfid == log.RFID:
                    exists = True
                    break

            if exists:
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
                    return HttpResponse('RFID Inválido\n')

        return HttpResponse('Operacion Terminada\n')

    else:
        return redirect('diners:diners')

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
        days_to_count = get_number_day()
        day_limit = days_to_count
        start_date_number = 0
        
        while start_date_number <= day_limit:
            day_object = {
                'date': str(start_datetime(days_to_count).date()),
                'day_name': None,
                'entries': None,
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
    title = 'Comensales del Dia'
    page_title = PAGE_TITLE

    context={
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'diners' : pag['queryset'],
        'paginator': pag,
        'total_diners': total_diners,
        'total_diners_today': total_diners_today,
        'diners_hour' : get_diners_per_hour(),
        'diners_week' : get_diners_actual_week(),
        'dates_range': get_dates_range(),
    }
    return render(request, template, context)    


# --------------------------- TEST ------------------------
def test(request):
    rfids = [
52661   ,
53253   ,
105407  ,
52582   ,
52462   ,
52496   ,
6718    ,
53936   ,
52658   ,
53184   ,
6693    ,
52005   ,
52565   ,
6656    ,
51324   ,
6765    ,
6784    ,
105202  ,
105147  ,
53288   ,
6564    ,
6676    ,
6685    ,
53261   ,
105157  ,
105165  ,
52843   ,
52687   ,
52796   ,
52253   ,
52769   ,
53006   ,
53864   ,
53903   ,
6655    ,
6829    ,
53937   ,
7910    ,
6946    ,
51610   ,
6707    ,
7989    ,
6950    ,
52054   ,
6527    ,
7987    ,
7985    ,
6713    ,
105231  ,
52183   ,
52539   ,
6876    ,
52525   ,
52617   ,
105103  ,
52812   ,
105429  ,
105107  ,
53255   ,
6785    ,
53259   ,
6853    ,
52561   ,
52252   ,
53157   ,
105007  ,
6705    ,
52093   ,
52569   ,
52662   ,
6682    ,
6768    ,
6681    ,
6877    ,
6573    ,
50454   ,
50566   ,
52453   ,
52602   ,
44876   ,
6772    ,
52103   ,
52558   ,
52523   ,
6888    ,
6948    ,
105105  ,
53177   ,
52450   ,
52640   ,
52600   ,
105108  ,
105168  ,
104914  ,
105162  ,
6550    ,
52559   ,
53090   ,
51750   ,
53058   ,
105156  ,
105020  ,
53270   ,
53162   ,
105130  ,
52610   ,
105042  ,
52573   ,
52648   ,
105059  ,
52502   ,
105137  ,
52497   ,
6788    ,
53273   ,
51046   ,
105418  ,
105098  ,
34704   ,
52614   ,
105067  ,
52621   ,
52592   ,
52574   ,
52390   ,
105054  ,
52448   ,
6798    ,
52556   ,
104911  ,
51376   ,
7924    ,
105074  ,
6562    ,
53285   ,
6709    ,
52623   ,
105043  ,
52647   ,
6641    ,
6687    ,
105002  ,
105118  ,
105245  ,
52799   ,
6871    ,
51858   ,
52981   ,
52312   ,
104920  ,
6587    ,
6578    ,
52612   ,
105060  ,
52591   ,
53004   ,
105201  ,
52576   ,
6874    ,
6777    ,
51863   ,
52793   ,
6801    ,
6879    ,
]


    for rfid in rfids:
        dt = naive_to_datetime(datetime(2017,3,23,13,30))
        rfid = str(rfid)
        if rfid is None:
            print('No se recibió RFID\n')
        else:
            access_logs = get_access_log(dt)
            exists = False
            
            for log in access_logs:
                if rfid == log.RFID:
                    exists = True
                    print('es identico...........')
                    break

            if exists:
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
                        print('Nuevo comensal\n')
                else:
                    print('RFID Inválido\n')

    return HttpResponse('Hola')