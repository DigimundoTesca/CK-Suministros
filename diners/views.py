
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
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


def diners(request):
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
        'dates_range': get_dates_range(),
    }
    return render(request, template, context)    


# --------------------------- TEST ------------------------
def test(request):
    rfids = [
        51733   ,
        51517   ,
        53157   ,
        50285   ,
        52653   ,
        105245  ,
        52812   ,
        53253   ,
        52015   ,
        51980   ,
        51804   ,
        53181   ,
        6797    ,
        53883   ,
        52803   ,
        52687   ,
        51542   ,
        6799    ,
        6712    ,
        6510    ,
        53188   ,
        105226  ,
        40713   ,
        52674   ,
        105433  ,
        7953    ,
        6914    ,
        105203  ,
        105143  ,
        6830    ,
        52135   ,
        52158   ,
        6915    ,
        53922   ,
        52631   ,
        6630    ,
        105026  ,
        6895    ,
        6787    ,
        53929   ,
        104941  ,
        105234  ,
        6695    ,
        105221  ,
        6897    ,
        6827    ,
        53853   ,
        53864   ,
        52999   ,
        51703   ,
        6741    ,
        6588    ,
        53933   ,
        53903   ,
        53855   ,
        53255   ,
        52843   ,
        52639   ,
        53275   ,
        6714    ,
        6717    ,
        7958    ,
        6672    ,
        105028  ,
        52102   ,
        6779    ,
        6719    ,
        105117  ,
        54398   ,
        105131  ,
        52611   ,
        52252   ,
        52424   ,
        53728   ,
        52312   ,
        52093   ,
        6767    ,
        52645   ,
        50566   ,
        6679    ,
        6681    ,
        52491   ,
        105093  ,
        105119  ,
        105147  ,
        6571    ,
        52496   ,
        53261   ,
        6620    ,
        104921  ,
        51919   ,
        53006   ,
        52613   ,
        6718    ,
        51664   ,
        52565   ,
        52808   ,
        6693    ,
        53184   ,
        105157  ,
        51925   ,
        53287   ,
        52448   ,
        52582   ,
        52599   ,
        6687    ,
        6877    ,
        50541   ,
        6851    ,
        6676    ,
        51376   ,
        35379   ,
        52624   ,
        105081  ,
        53292   ,
        6564    ,
        7963    ,
        52522   ,
        53877   ,
        51693   ,
        52539   ,
        6720    ,
        52482   ,
        7988    ,
        105007  ,
        52419   ,
        6876    ,
        6707    ,
        51610   ,
        52054   ,
        53941   ,
        6713    ,
        104920  ,
        53034   ,
        6708    ,
        52600   ,
        105241  ,
        6552    ,
        6705    ,
        105202  ,
        51324   ,
        6891    ,
        52569   ,
        52453   ,
        53162   ,
        105107  ,
        52525   ,
        105075  ,
        105059  ,
        105042  ,
        52585   ,
        53270   ,
        52502   ,
        34704   ,
        51046   ,
        52561   ,
        53172   ,
        6880    ,
        6550    ,
        105162  ,
        52799   ,
        105429  ,
        53872   ,
        105088  ,
        51858   ,
        6871    ,
        6586    ,
        105019  ,
        7910    ,
        105069  ,
        105418  ,
        105168  ,
        105432  ,
        105156  ,
        105130  ,
        105098  ,
        6749    ,
        52610   ,
        52577   ,
        52573   ,
        6888    ,
        6626    ,
        52627   ,
        6709    ,
        53273   ,
        52527   ,
        6878    ,
        53285   ,
        52621   ,
        52614   ,
        52574   ,
        6788    ,
        52451   ,
        6578    ,
        52103   ,
        52602   ,
        105043  ,
        105137  ,
        105113  ,
        105072  ,
        126326  ,
        138298  ,
        105118  ,
        105002  ,
        6647    ,
        6882    ,
        105193  ,
        6645    ,
        6613    ,
        52589   ,
        139651  ,
        84965   ,
        156803  ,
        153633  ,
        52550   ,
        152098  ,
        143348  ,
        150912  ,
        58610   ,
        53177   ,
        6665    ,
        53793   ,
        53259   ,
        53254   ,
        52640   ,
        52649   ,
        6795    ,
        51874   ,
        6690    ,
        105447  ,
        53892   ,
        6912    ,
        7952    ,
        105448  ,
        105060  ,
        52591   ,
        105238  ,
        6920    ,
        52612   ,
        105054  ,
        6701    ,
        6783    ,
        105199  ,
        52576   ,
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