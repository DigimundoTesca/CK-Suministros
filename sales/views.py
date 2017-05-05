import json, pytz
from datetime import datetime, date, timedelta, time

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Max, Min

from branchoffices.models import CashRegister
from cloudkitchen.settings.base import PAGE_TITLE
from helpers import Helper
from products.models import Cartridge, PackageCartridge, PackageCartridgeRecipe, \
                            ExtraIngredient
from sales.models import Ticket, TicketDetail, TicketExtraIngredient
from users.models import User as UserProfile


class SalesHelper(object):
    def __init__(self):
        self.__all_tickets = None
        self.__all_tickets_details = None
        super(SalesHelper, self).__init__()

    def set_all_tickets(self):
        self.__all_tickets = Ticket.objects.select_related('seller').all()

    def set_all_tickets_details(self):
        self.__all_tickets_details = TicketDetail.objects.\
            select_related('ticket').\
            select_related('cartridge'). \
            select_related('package_cartridge'). \
            all()

    def get_all_tickets(self):
        return self.__all_tickets

    def get_all_tickets_details(self):
        return self.__all_tickets_details


# -------------------------------------  Sales -------------------------------------
@login_required(login_url='users:login')
def sales(request):
    helper = Helper()
    sales_helper = SalesHelper()
    sales_helper.set_all_tickets()
    sales_helper.set_all_tickets_details()

    def get_years_list():
        """
        Returns a list of all the years in which there have been sales
        """
        years_list = []

        for ticket in sales_helper.get_all_tickets():
            if ticket.created_at.year not in years_list:
                years_list.append(ticket.created_at.year)

        return years_list

    def get_dates_range():
        """
        Returns a JSON with a years list.
        The years list contains years objects that contains a weeks list
            and the Weeks list contains a weeks objects with two attributes: 
            start date and final date. Ranges of each week.
        """
        try:
            min_year = sales_helper.get_all_tickets().aggregate(Min('created_at'))['created_at__min'].year
            max_year = sales_helper.get_all_tickets().aggregate(Max('created_at'))['created_at__max'].year
            years_list = []  # [2015:object, 2016:object, 2017:object, ...]
        except:
            min_year = datetime.now().year
            max_year = datetime.now().year
            years_list = []  # [2015:object, 2016:object, 2017:object, ...]

        while max_year >= min_year:
            year_object = {  # 2015:object or 2016:object or 2017:object ...
                'year': max_year,
                'weeks_list': []
            }

            tickets_per_year = sales_helper.get_all_tickets().filter(
                created_at__range=[helper.naive_to_datetime(date(max_year, 1, 1)),
                                   helper.naive_to_datetime(date(max_year, 12, 31))])
            for ticket in tickets_per_year:
                if len(year_object['weeks_list']) == 0:
                    """
                    Creates a new week_object in the weeks_list of the actual year_object
                    """
                    week_object = {
                        'week_number': ticket.created_at.isocalendar()[1],
                        'start_date': ticket.created_at.date().strftime("%d-%m-%Y"),
                        'end_date': ticket.created_at.date().strftime("%d-%m-%Y"),
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

                        if week_object['week_number'] == ticket.created_at.isocalendar()[1]:
                            # There's a same week number
                            existing_week = True
                            if datetime.strptime(week_object['start_date'],
                                                 "%d-%m-%Y").date() > ticket.created_at.date():
                                exists = True
                                week_object['start_date'] = ticket.created_at.date().strftime("%d-%m-%Y")
                            elif datetime.strptime(week_object['end_date'],
                                                   "%d-%m-%Y").date() < ticket.created_at.date():
                                week_object['end_date'] = ticket.created_at.date().strftime("%d-%m-%Y")

                            existing_week = True
                            break

                    if not existing_week:
                        # There's a different week number
                        week_object = {
                            'week_number': ticket.created_at.isocalendar()[1],
                            'start_date': ticket.created_at.date().strftime("%d-%m-%Y"),
                            'end_date': ticket.created_at.date().strftime("%d-%m-%Y"),
                        }
                        year_object['weeks_list'].append(week_object)

                        # End else
            years_list.append(year_object)
            max_year -= 1
        # End while
        return json.dumps(years_list)

    def get_sales(start_date, final_date):
        """
        Gets the following properties for each week's day: Name, Date and Earnings
        """
        limit_day = start_date + timedelta(days=1)
        total_days = (final_date - start_date).days
        week_sales_list = []
        count = 1
        total_earnings = 0

        while count <= total_days:
            tickets = sales_helper.get_all_tickets().filter(created_at__range=[start_date, limit_day])
            day_object = {
                'date': str(start_date.date().strftime('%d-%m-%Y')),
                'day_name': None,
                'earnings': None,
                'number_day': helper.get_number_day(start_date),
            }

            for ticket in tickets:
                for ticket_detail in sales_helper.get_all_tickets_details():
                    if ticket_detail.ticket == ticket:
                        total_earnings += ticket_detail.price

            day_object['day_name'] = helper.get_name_day(start_date.date())
            day_object['earnings'] = str(total_earnings)

            week_sales_list.append(day_object)

            # Reset datas
            limit_day += timedelta(days=1)
            start_date += timedelta(days=1)
            total_earnings = 0
            count += 1

        return week_sales_list

    def get_sales_actual_week():
        """
        Gets the following properties for each week's day: Name, Date and Earnings
        """
        week_sales_list = []
        total_earnings = 0
        days_to_count = helper.get_number_day(datetime.now())
        day_limit = days_to_count
        start_date_number = 0

        while start_date_number <= day_limit:
            day_object = {
                'date': str(helper.start_datetime(days_to_count).date().strftime('%d-%m-%Y')),
                'day_name': None,
                'earnings': None,
                'number_day': helper.get_number_day(helper.start_datetime(days_to_count).date()),
            }

            tickets = sales_helper.get_all_tickets().filter(created_at__range=[helper.start_datetime(days_to_count), helper.end_datetime(days_to_count)])

            for ticket in tickets:
                for ticket_detail in sales_helper.get_all_tickets_details():
                    if ticket_detail.ticket == ticket:
                        total_earnings += ticket_detail.price

            day_object['earnings'] = str(total_earnings)
            day_object['day_name'] = helper.get_name_day(helper.start_datetime(days_to_count).date())

            week_sales_list.append(day_object)

            # restarting counters
            days_to_count -= 1
            total_earnings = 0
            start_date_number += 1

        return json.dumps(week_sales_list)

    def get_tickets_today():
        tickets_details = TicketDetail.objects.select_related(
            'ticket', 'ticket__seller', 'cartridge', 'package_cartridge').filter()
        tickets = Ticket.objects.filter(created_at__gte=helper.naive_to_datetime(date.today()))
        tickets_list = []

        for ticket in tickets:
            ticket_object = {
                'ticket_parent': ticket,
                'order_number': ticket.order_number,
                'cartridges': [],
                'packages': [],
                'total': Decimal(0.00),
            }

            for ticket_details in tickets_details:
                if ticket_details.ticket == ticket:
                    if ticket_details.cartridge:
                        cartridge_object = {
                            'cartridge': ticket_details.cartridge,
                            'quantity': ticket_details.quantity
                        }
                        ticket_object['cartridges'].append(cartridge_object)
                        ticket_object['total'] += ticket_details.price
                    elif ticket_details.package_cartridge:
                        package_cartridge_object = {
                            'package': ticket_details.package_cartridge,
                            'quantity': ticket_details.quantity
                        }
                        ticket_object['packages'].append(package_cartridge_object)
                        ticket_object['total'] += ticket_details.price

            tickets_list.append(ticket_object)

        return tickets_list

    def get_tickets(initial_date, final_date):
        tickets = sales_helper.get_all_tickets().filter(created_at__range=(initial_date, final_date)).order_by('-created_at')
        tickets_details = sales_helper.get_all_tickets_details()
        tickets_list = []

        for ticket in tickets:
            ticket_object = {
                'id': ticket.id,
                'order_number': ticket.order_number,
                'created_at': datetime.strftime(ticket.created_at, "%B %d, %Y, %H:%M:%S %p"),
                'seller': ticket.seller.username,
                'ticket_details': {
                    'cartridges': [],
                    'packages': [],
                },
                'total': 0,
            }

            for ticket_detail in tickets_details:
                if ticket_detail.ticket == ticket:
                    ticket_detail_object = {}
                    if ticket_detail.cartridge:
                        ticket_detail_object = {
                            'name': ticket_detail.cartridge.name,
                            'quantity': ticket_detail.quantity,
                            'price': float(ticket_detail.price),
                        }
                        ticket_object['ticket_details']['cartridges'].append(ticket_detail_object)
                    elif ticket_detail.package_cartridge:
                        ticket_detail_object = {
                            'name': ticket_detail.package_cartridge.name,
                            'quantity': ticket_detail.quantity,
                            'price': float(ticket_detail.price),
                        }
                        ticket_object['ticket_details']['packages'].append(ticket_detail_object)

                    ticket_object['total'] += float(ticket_detail.price)

                    try:
                        ticket_object['ticket_details'].append(ticket_detail_object)
                    except Exception as e:
                        pass
            ticket_object['total'] = str(ticket_object['total'])
            tickets_list.append(ticket_object)
        return tickets_list

    if request.method == 'POST':
        if request.POST['type'] == 'sales_day':
            """
            Returns a list with objects:
            Each object has the following characteristics
            """
            sales_day_list = []
            start_day = helper.naive_to_datetime(datetime.strptime(request.POST['date'], '%d-%m-%Y').date())
            end_date = helper.naive_to_datetime(start_day + timedelta(days=1))
            tickets_objects = sales_helper.get_all_tickets().filter(created_at__range=[start_day, end_date])

            for ticket in tickets_objects:
                """
                Filling in the sales list of the day
                """
                earnings_sale_object = {
                    'id_ticket': ticket.id,
                    'datetime': timezone.localtime(ticket.created_at),
                    'earnings': 0
                }
                for ticket_detail in sales_helper.get_all_tickets_details():
                    if ticket_detail.ticket == ticket:
                        earnings_sale_object['earnings'] += ticket_detail.price
                sales_day_list.append(earnings_sale_object)
            return JsonResponse({'sales_day_list': sales_day_list})

        if request.POST['type'] == 'ticket_details':
            ticket_id = int(request.POST['ticket_id'])
            ticket_object = {
                'ticket_id': ticket_id,
                'ticket_order': '',
                'cartridges': [],
                'packages': [],
            }

            # Get cartridges details
            for ticket_detail in sales_helper.get_all_tickets_details():
                if ticket_detail.ticket.id == ticket_id:
                    ticket_object['ticket_order'] = ticket_detail.ticket.order_number;

                    if ticket_detail.cartridge:
                        cartridge_object = {
                            'name': ticket_detail.cartridge.name,
                            'quantity': ticket_detail.quantity,
                            'total': ticket_detail.price
                        }
                        ticket_object['cartridges'].append(cartridge_object)
                    elif ticket_detail.package_cartridge:
                        cartridges_list = []
                        package_cartridge_recipe = PackageCartridgeRecipe.objects.filter(
                            package_cartridge=ticket_detail.package_cartridge)

                        for cartridge_recipe in package_cartridge_recipe:
                            cartridges_list.append(cartridge_recipe.cartridge.name)

                        package_cartridge_object = {
                            'cartridges': cartridges_list,
                            'quantity': ticket_detail.quantity,
                            'total': ticket_detail.price
                        }
                        ticket_object['packages'].append(package_cartridge_object)

            return JsonResponse({'ticket_details': ticket_object})

        if request.POST['type'] == 'tickets':
            tickets_objects_list = []

            for ticket in sales_helper.get_all_tickets():
                for ticket_detail in sales_helper.get_all_tickets_details():
                    if ticket_detail.ticket == ticket:
                        ticket_object = {
                            'ID': ticket.id,
                            'Fecha': timezone.localtime(ticket.created_at).date(),
                            'Hora': timezone.localtime(ticket.created_at).time(),
                            'Vendedor': ticket.seller.username,
                        }
                        if ticket.payment_type == 'CA':
                            ticket_object['Tipo de Pago'] = 'Efectivo'
                        else:
                            ticket_object['Tipo de Pago'] = 'Crédito'
                        if ticket_detail.cartridge:
                            ticket_object['Producto'] =  ticket_detail.cartridge.name
                        else:
                            ticket_object['Producto'] =  None
                        if ticket_detail.package_cartridge:
                            ticket_object['Paquete'] = ticket_detail.package_cartridge.name
                        else:
                            ticket_object['Paquete'] = None
                        ticket_object['Cantidad'] = ticket_detail.quantity
                        ticket_object['Total'] = ticket_detail.price
                        ticket_object['Precio Unitario'] = ticket_detail.price / ticket_detail.quantity

                        tickets_objects_list.append(ticket_object)

            return JsonResponse({'ticket': tickets_objects_list})

        if request.POST['type'] == 'sales_week':
            initial_date = request.POST['dt_week'].split(',')[0]
            final_date = request.POST['dt_week'].split(',')[1]
            initial_date = helper.parse_to_datetime(initial_date)
            final_date = helper.parse_to_datetime(final_date) + timedelta(days=1)

            sales = get_sales(initial_date, final_date)
            tickets = get_tickets(initial_date, final_date)
            data = {
                'sales': sales,
                'tickets': tickets,
                'week_number': helper.get_week_number(initial_date)
            }
            return JsonResponse(data)

    # Any other request method:
    template = 'sales/sales.html'
    title = 'Registro de Ventas'
    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'actual_year': datetime.now().year,
        'sales_week': get_sales_actual_week(),
        'today_name': helper.get_name_day(datetime.now()),
        'today_number': helper.get_number_day(datetime.now()),
        'week_number': helper.get_week_number(date.today()),
        'tickets': get_tickets_today(),
        'dates_range': get_dates_range(),

    }
    return render(request, template, context)


@login_required(login_url='users:login')
def delete_sale(request):
    if request.method == 'POST':
        ticket_id = request.POST['ticket_id']
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.delete()
        return JsonResponse({'result': 'excelente!'})


@login_required(login_url='users:login')
def new_sale(request):
    helper = Helper()
    if request.method == 'POST':
        if request.POST['ticket']:
            username = request.user
            user_profile_object = get_object_or_404(UserProfile, username=username)
            cash_register = CashRegister.objects.first()
            ticket_detail_json_object = json.loads(request.POST.get('ticket'))
            payment_type = ticket_detail_json_object['payment_type']
            order_number = 1
            """ 
            Gets the tickets in the week and returns n + 1 
            where n is the Ticket.order_number biggest for the current week
            TODO:
            1. Get tickets in the current week range
            2. Search the ticket with the largest order_number atribute
            3. save the 'new_ticket_object' with the new atribute (n + 1)
            4. Save the new object
            """

            tickets = Ticket.objects.filter(created_at__gte=datetime.now() - timedelta(days=helper.get_number_day(datetime.now())))

            for ticket in tickets:
                order_number_ticket = ticket.order_number
                if order_number_ticket >= order_number:
                    order_number = order_number_ticket + 1

            new_ticket_object = Ticket(
                cash_register=cash_register, seller=user_profile_object,
                payment_type=payment_type, order_number=order_number)
            new_ticket_object.save()

            """
            Saves the tickets details for cartridges
            """
            for ticket_detail in ticket_detail_json_object['cartridges']:
                cartridge_object = get_object_or_404(Cartridge, id=ticket_detail['id'])
                quantity = ticket_detail['quantity']
                price = ticket_detail['price']
                new_ticket_detail_object = TicketDetail(
                    ticket=new_ticket_object,
                    cartridge=cartridge_object,
                    quantity=quantity,
                    price=price
                )
                new_ticket_detail_object.save()

            for ticket_detail in ticket_detail_json_object['extra_ingredients_cartridges']:
                cartridge_object = get_object_or_404(Cartridge, id=ticket_detail['cartridge_id'])
                quantity = ticket_detail['quantity']
                price = ticket_detail['price']
                new_ticket_detail_object = TicketDetail(
                    ticket=new_ticket_object,
                    cartridge=cartridge_object,
                    quantity=quantity,
                    price=price
                )
                new_ticket_detail_object.save()

                for ingredient in ticket_detail['extra_ingredients']:
                    extra_ingredient_object = ExtraIngredient.objects.get(id=ingredient['id'])
                    new_extra_ingredient_object = TicketExtraIngredient(
                        ticket_detail=new_ticket_detail_object,
                        extra_ingredient=extra_ingredient_object,
                        price=ingredient['cost']
                        )
                    new_extra_ingredient_object.save()

            for ticket_detail_package in ticket_detail_json_object['packages']:
                """
                Saves the tickets details for package cartridges
                """
                package_object = get_object_or_404(PackageCartridge, id=ticket_detail_package['id'])
                quantity = ticket_detail_package['quantity']
                price = ticket_detail_package['price']
                new_ticket_detail_object = TicketDetail(
                    ticket=new_ticket_object,
                    package_cartridge=package_object,
                    quantity=quantity,
                    price=price
                )
                new_ticket_detail_object.save()

            json_response = {
                'status': 'ready',
                'ticket_id': new_ticket_object.id,
                'ticket_order': new_ticket_object.order_number,
            }
            return JsonResponse(json_response)

        return JsonResponse({'status': 'error'})

    else:
        path = request.get_full_path().split('/')[3]
        if path == 'breakfast':
            template = 'new/breakfast.html'
            title = 'Vender Desayuno'

        else:
            template = 'new/food.html'
            title = 'Vender Comida'

        cartridges_list = Cartridge.objects.all().order_by('name')
        package_cartridges = PackageCartridge.objects.all().order_by('name')
        extra_ingredients = ExtraIngredient.objects.all().prefetch_related('ingredient');
        extra_ingredients_products_list = []

        for cartridge in cartridges_list:
            cartridge_object = {
                'id': cartridge.id,
                'name': cartridge.name,
                'extra_ingredients': [],
            }
            for ingredient in extra_ingredients:
                if cartridge == ingredient.cartridge:
                    ingredient_object = {
                        'id': ingredient.id,
                        'name': ingredient.ingredient.name,
                        'image': ingredient.image.url,
                        'cost': str(ingredient.cost),
                    }
                    cartridge_object['extra_ingredients'].append(ingredient_object)
            if len(cartridge_object['extra_ingredients']) > 0:
                extra_ingredients_products_list.append(cartridge_object)


        context = {
            'title': PAGE_TITLE + ' | ' + title,
            'page_title': title,
            'cartridges': cartridges_list,
            'package_cartridges': package_cartridges,
            'extra_ingredients': extra_ingredients,
            'extra_ingredients_products_list': extra_ingredients_products_list,
            'extra_ingredients_products_list_json': json.dumps(extra_ingredients_products_list),
        }
        return render(request, template, context)


# -------------------------------- Test ------------------------------
def test(request):
    template = 'sales/test.html'

    tickets_details = TicketDetail.objects.select_related('ticket', 'ticket__seller', 'cartridge','package_cartridge').filter()
    tickets = Ticket.objects.all()
    tickets_list = []

    for ticket in tickets:
        ticket_object = {
            'ticket_parent': ticket,
            'cartridges': [],
            'packages': [],
            'total': Decimal(0.00),
        }

        for ticket_details in tickets_details:
            if ticket_details.ticket == ticket:
                if ticket_details.cartridge:
                    cartridge_object = {
                        'cartridge': ticket_details.cartridge,
                        'quantity': ticket_details.quantity
                    }
                    ticket_object['cartridges'].append(cartridge_object)
                    ticket_object['total'] += ticket_details.price
                elif ticket_details.package_cartridge:
                    package_cartridge_object = {
                        'package': ticket_details.package_cartridge,
                        'quantity': ticket_details.quantity
                    }
                    ticket_object['packages'].append(package_cartridge_object)
                    ticket_object['total'] += ticket_details.price

        tickets_list.append(ticket_object)

    context = {
        'tickets': tickets_list,
    }

    return render(request, template, context)