import json
import pytz

from datetime import datetime, date, timedelta, time
from decimal import Decimal
from django.db.models import Min, Max
from django.utils import timezone

from diners.models import Diner, AccessLog
from kitchen.models import ProcessedProduct, Warehouse
from products.models import Cartridge, PackageCartridge, Supply, ExtraIngredient, PackageCartridgeRecipe, \
    CartridgeRecipe
from sales.models import Ticket, TicketDetail, TicketExtraIngredient


class Helper(object):
    def __init__(self):
        self.tz = pytz.timezone('America/Mexico_City')
        self.days_list = {
            'MONDAY': 'Lunes',
            'TUESDAY': 'Martes',
            'WEDNESDAY': 'Miércoles',
            'THURSDAY': 'Jueves',
            'FRIDAY': 'Viernes',
            'SATURDAY': 'Sábado',
            'SUNDAY': 'Domingo'
        }
        super(Helper, self).__init__()

    def naive_to_datetime(self, nd):
        if type(nd) == datetime:
            if nd.tzinfo is not None and nd.tzinfo.utcoffset(nd) is not None:  # Is Aware
                return nd
            else:  # Is Naive
                return self.tz.localize(nd)

        elif type(nd) == date:
            d = nd
            t = time(0, 0)
            new_date = datetime.combine(d, t)
            return pytz.timezone('America/Mexico_City').localize(new_date)

    def start_datetime(self, back_days):
        start_date = date.today() - timedelta(days=back_days)
        return self.naive_to_datetime(start_date)

    def end_datetime(self, back_days):
        end_date = self.start_datetime(back_days) + timedelta(days=1)
        return self.naive_to_datetime(end_date)

    def parse_to_datetime(self, dt):
        day = int(dt.split('-')[0])
        month = int(dt.split('-')[1])
        year = int(dt.split('-')[2])
        parse_date = date(year, month, day)
        return self.naive_to_datetime(parse_date)

    def are_equal_lists(self, list_1, list_2):
        """
         Checks if two lists are identical
        """
        list_1 = self.items_list_to_int(list_1)
        list_2 = self.items_list_to_int(list_2)

        list_1.sort()
        list_2.sort()

        if len(list_1) != len(list_2):
            return False
        else:
            for element in range(0, len(list_1)):
                if list_1[element] != list_2[element]:
                    return False

        return True

    def get_name_day(self, datetime_now):
        name_day = date(datetime_now.year, datetime_now.month, datetime_now.day)
        return self.days_list[name_day.strftime('%A').upper()]

    def get_number_day(self, dt):
        days = {
            'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sábado': 5, 'Domingo': 6,
        }
        return days[self.get_name_day(dt)]

    @staticmethod
    def get_week_number(dt):
        return dt.isocalendar()[1]

    @staticmethod
    def items_list_to_int(list_to_cast):
        """
        Evaluates each of the elements of the list received and casts them to integers
        """
        cast_list = []
        for item in range(0, len(list_to_cast)):
            cast_list.append(int(list_to_cast[item]))

        return cast_list


class SalesHelper(object):
    def __init__(self):
        self.__all_tickets = None
        self.__all_tickets_details = None
        self.__all_extra_ingredients = None
        super(SalesHelper, self).__init__()

    def set_all_tickets(self):
        self.__all_tickets = Ticket.objects.select_related('seller').all()

    def set_all_tickets_details(self):
        self.__all_tickets_details = TicketDetail.objects.\
            select_related('ticket').\
            select_related('cartridge'). \
            select_related('ticket__seller'). \
            select_related('package_cartridge'). \
            all()

    def set_all_extra_ingredients(self):
        self.__all_extra_ingredients = TicketExtraIngredient.objects.\
            select_related('ticket_detail'). \
            select_related('extra_ingredient'). \
            select_related('extra_ingredient__ingredient'). \
            all()

    def get_all_tickets(self):
        """        
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_tickets is None:
            self.set_all_tickets()
        return self.__all_tickets

    def get_all_tickets_details(self):
        """        
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_tickets_details is None:
            self.set_all_tickets_details()
        return self.__all_tickets_details

    def get_all_extra_ingredients(self):
        """        
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_extra_ingredients is None:
            self.set_all_extra_ingredients()
        return self.__all_extra_ingredients

    def get_years_list(self):
        """
        Returns a list of all the years in which there have been sales
        """
        years_list = []

        for ticket in self.get_all_tickets():
            if ticket.created_at.year not in years_list:
                years_list.append(ticket.created_at.year)

        return years_list

    def get_tickets_today_list(self):
        helper = Helper()

        tickets_list = []
        filtered_tickets = self.get_all_tickets().filter(created_at__gte=helper.naive_to_datetime(date.today()))

        for ticket in filtered_tickets:
            ticket_object = {
                'ticket_parent': ticket,
                'order_number': ticket.order_number,
                'cartridges': [],
                'packages': [],
                'total': Decimal(0.00),
            }

            for ticket_details in self.get_all_tickets_details():
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

    def get_dates_range_json(self):
        """
        Returns a JSON with a years list.
        The years list contains years objects that contains a weeks list
            and the Weeks list contains a weeks objects with two attributes: 
            start date and final date. Ranges of each week.
        """
        helper = Helper()
        try:
            min_year = self.get_all_tickets().aggregate(Min('created_at'))['created_at__min'].year
            max_year = self.get_all_tickets().aggregate(Max('created_at'))['created_at__max'].year
            years_list = []  # [2015:object, 2016:object, 2017:object, ...]
        except:
            min_year = datetime.now().year
            max_year = datetime.now().year
            years_list = []  # [2015:object, 2016:object, 2017:object, ...]

        while max_year >= min_year:
            year_object = {  # 2015:object or 2016:object or 2017:object ...
                'year': max_year,
                'weeks_list': [],
            }

            tickets_per_year = self.get_all_tickets().filter(
                created_at__range=[helper.naive_to_datetime(date(max_year, 1, 1)),
                                   helper.naive_to_datetime(date(max_year, 12, 31))])
            for ticket_item in tickets_per_year:
                if len(year_object['weeks_list']) == 0:
                    """
                    Creates a new week_object in the weeks_list of the actual year_object
                    """
                    week_object = {
                        'week_number': ticket_item.created_at.isocalendar()[1],
                        'start_date': ticket_item.created_at.date().strftime("%d-%m-%Y"),
                        'end_date': ticket_item.created_at.date().strftime("%d-%m-%Y"),
                    }
                    year_object['weeks_list'].append(week_object)
                    # End if
                else:
                    """
                    Validates if exists some week with an similar week_number of the actual year
                    If exists a same week in the list validates the start_date and the end_date,
                    In each case valid if there is an older start date or a more current end date 
                        if it is the case, update the values.
                    Else creates a new week_object with the required week number
                    """
                    existing_week = False
                    for week_object in year_object['weeks_list']:

                        if week_object['week_number'] == ticket_item.created_at.isocalendar()[1]:
                            # There's a same week number
                            if datetime.strptime(week_object['start_date'],
                                                 "%d-%m-%Y").date() > ticket_item.created_at.date():
                                week_object['start_date'] = ticket_item.created_at.date().strftime("%d-%m-%Y")
                            elif datetime.strptime(week_object['end_date'],
                                                   "%d-%m-%Y").date() < ticket_item.created_at.date():
                                week_object['end_date'] = ticket_item.created_at.date().strftime("%d-%m-%Y")

                            existing_week = True
                            break

                    if not existing_week:
                        # There's a different week number
                        week_object = {
                            'week_number': ticket_item.created_at.isocalendar()[1],
                            'start_date': ticket_item.created_at.date().strftime("%d-%m-%Y"),
                            'end_date': ticket_item.created_at.date().strftime("%d-%m-%Y"),
                        }
                        year_object['weeks_list'].append(week_object)

                        # End else
            years_list.append(year_object)
            max_year -= 1
        # End while
        return json.dumps(years_list)

    def get_sales_list(self, start_dt, final_dt):
        """
        Gets the following properties for each week's day: Name, Date and Earnings
        """
        helper = Helper()
        limit_day = start_dt + timedelta(days=1)
        total_days = (final_dt - start_dt).days
        week_sales_list = []
        count = 1
        total_earnings = 0

        while count <= total_days:
            day_tickets = self.get_all_tickets().filter(created_at__range=[start_dt, limit_day])
            day_object = {
                'date': str(start_dt.date().strftime('%d-%m-%Y')),
                'day_name': None,
                'earnings': None,
                'number_day': helper.get_number_day(start_dt),
            }

            for ticket_item in day_tickets:
                for ticket_detail_item in self.get_all_tickets_details():
                    if ticket_detail_item.ticket == ticket_item:
                        total_earnings += ticket_detail_item.price

            day_object['day_name'] = helper.get_name_day(start_dt.date())
            day_object['earnings'] = str(total_earnings)

            week_sales_list.append(day_object)

            # Reset data
            limit_day += timedelta(days=1)
            start_dt += timedelta(days=1)
            total_earnings = 0
            count += 1

        return week_sales_list

    def get_sales_actual_week(self):
        """
        Gets the following properties for each week's day: Name, Date and Earnings
        """
        helper = Helper()
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

            day_tickets = self.get_all_tickets().filter(
                created_at__range=[helper.start_datetime(days_to_count), helper.end_datetime(days_to_count)])

            for ticket_item in day_tickets:
                for ticket_detail_item in self.get_all_tickets_details():
                    if ticket_detail_item.ticket == ticket_item:
                        total_earnings += ticket_detail_item.price

            day_object['earnings'] = str(total_earnings)
            day_object['day_name'] = helper.get_name_day(helper.start_datetime(days_to_count).date())

            week_sales_list.append(day_object)

            # restarting counters
            days_to_count -= 1
            total_earnings = 0
            start_date_number += 1

        return json.dumps(week_sales_list)

    def get_tickets(self, initial_date, final_date):
        all_tickets = self.get_all_tickets().filter(
            created_at__range=(initial_date, final_date)).order_by('-created_at')
        all_tickets_details = self.get_all_tickets_details()
        tickets_list = []

        for ticket in all_tickets:
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

            for ticket_detail in all_tickets_details:
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


class ProductsHelper(object):
    def __init__(self):
        super(ProductsHelper, self).__init__()
        self.__all_cartridges = None
        self.__all_packages_cartridges = None
        self.__all_supplies = None
        self.__all_extra_ingredients = None
        self.__all_cartridges_recipes = None
        self.__all_packages_cartridges_recipes = None

    def set_all_supplies(self):
        self.__all_supplies = Supply.objects.all()

    def set_all_cartridges(self):
        self.__all_cartridges = Cartridge.objects.all()

    def set_all_packages_cartridges(self):
        self.__all_packages_cartridges = PackageCartridge.objects.all()

    def set_all_cartridges_recipes(self):
        self.__all_cartridges_recipes = CartridgeRecipe.objects. \
            select_related('cartridge'). \
            select_related('supply'). \
            all()

    def set_all_package_cartridges_recipes(self):
        self.__all_packages_cartridges_recipes = PackageCartridgeRecipe.objects. \
            select_related('package_cartridge'). \
            select_related('cartridge'). \
            all()

    def set_all_extra_ingredients(self):
        self.__all_extra_ingredients = ExtraIngredient.objects.\
            select_related('ingredient').\
            select_related('cartridge'). \
            all()

    def get_all_supplies(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_supplies is None:
            self.set_all_supplies()
        return self.__all_supplies

    def get_all_cartridges(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_cartridges is None:
            self.set_all_cartridges()
        return self.__all_cartridges

    def get_all_packages_cartridges(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_packages_cartridges is None:
            self.set_all_packages_cartridges()
        return self.__all_packages_cartridges

    def get_all_extra_ingredients(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_extra_ingredients is None:
            self.set_all_extra_ingredients()

        return self.__all_extra_ingredients

    def get_all_cartridges_recipes(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_cartridges_recipes is None:
            self.set_all_cartridges_recipes()

        return self.__all_cartridges_recipes

    def get_all_packages_cartridges_recipes(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_packages_cartridges_recipes is None:
            self.set_all_package_cartridges_recipes()

        return self.__all_packages_cartridges_recipes


class DinersHelper(object):
    def __init__(self):
        self.__all_diners = None
        self.__all_access_logs = None
        super(DinersHelper, self).__init__()

    def get_all_diners_logs_list(self, initial_date, final_date):
        helper = Helper()
        diners_logs_list = []

        diners_logs_objects = self.get_access_logs(initial_date, final_date)

        for diner_log in diners_logs_objects:
            diner_log_object = {
                'rfid': diner_log.RFID,
                'access': datetime.strftime(timezone.localtime(diner_log.access_to_room), "%B %d, %I, %H:%M:%S %p"),
                'number_day': helper.get_number_day(diner_log.access_to_room),
            }
            if diner_log.diner:
                diner_log_object['SAP'] = diner_log.diner.employee_number
                diner_log_object['name'] = diner_log.diner.name
            else:
                diner_log_object['SAP'] = ''
                diner_log_object['name'] = ''
            diners_logs_list.append(diner_log_object)
        return diners_logs_list

    def get_weeks_entries(self, initial_dt, final_dt):
        """
        Gets the following properties for each week's day: Name, Date and Earnings
        """
        if self.__all_access_logs is None:
            self.set_all_access_logs()

        helper = Helper()
        limit_day = initial_dt + timedelta(days=1)
        weeks_list = []
        count = 1
        total_days = (final_dt - initial_dt).days

        while count <= total_days:
            diners_entries = self.__all_access_logs.filter(access_to_room__range=[initial_dt, limit_day])
            day_object = {
                'date': str(timezone.localtime(initial_dt).date().strftime('%d-%m-%Y')),
                'day_name': helper.get_name_day(initial_dt.date()), 'entries': diners_entries.count(),
                'number_day': helper.get_number_day(initial_dt)}

            weeks_list.append(day_object)

            # Reset data
            limit_day += timedelta(days=1)
            initial_dt += timedelta(days=1)
            count += 1

        return weeks_list

    def get_access_logs(self, initial_date, final_date):
        """
        :rtype: django.db.models.query.QuerySet 
        """
        if self.__all_access_logs is None:
            self.set_all_access_logs()

        return self.__all_access_logs. \
            filter(access_to_room__range=(initial_date, final_date)). \
            order_by('-access_to_room')

    def get_access_logs_today(self):
        """
        :rtype: django.db.models.query.QuerySet 
        """
        if self.__all_access_logs is None:
            self.set_all_access_logs()
        helper = Helper()
        year = int(datetime.now().year)
        month = int(datetime.now().month)
        day = int(datetime.now().day)
        initial_date = helper.naive_to_datetime(date(year, month, day))
        final_date = helper.naive_to_datetime(initial_date + timedelta(days=1))
        return self.__all_access_logs. \
            filter(access_to_room__range=(initial_date, final_date)). \
            order_by('-access_to_room')

    def get_all_access_logs(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_access_logs is None:
            self.set_all_access_logs()
        return self.__all_access_logs

    def get_diners_per_hour_json(self):
        hours_list = []
        hours_to_count = 12
        start_hour = 5
        customer_count = 0
        logs = self.get_access_logs_today()

        while start_hour <= hours_to_count:
            hour = {'count': None, }
            for log in logs:
                log_datetime = str(log.access_to_room)
                log_date, log_time = log_datetime.split(" ")

                if log_time.startswith("0" + str(start_hour)):
                    customer_count += 1
                hour['count'] = customer_count

            hours_list.append(hour)
            customer_count = 0
            start_hour += 1

        return json.dumps(hours_list)

    def get_diners_actual_week(self):
        if self.__all_access_logs is None:
            self.set_all_access_logs()
        helper = Helper()
        week_diners_list = []
        total_entries = 0
        days_to_count = helper.get_number_day(date.today())
        day_limit = days_to_count
        start_date_number = 0

        while start_date_number <= day_limit:
            day_object = {
                'date': str(helper.start_datetime(days_to_count).date().strftime('%d-%m-%Y')),
                'day_name': None,
                'entries': None,
                'number_day': helper.get_number_day(helper.start_datetime(days_to_count).date())
            }

            logs = self.__all_access_logs. \
                filter(access_to_room__range=[helper.start_datetime(days_to_count), helper.end_datetime(days_to_count)])

            for _ in logs:
                total_entries += 1

            day_object['entries'] = str(total_entries)
            day_object['day_name'] = helper.get_name_day(helper.start_datetime(days_to_count).date())

            week_diners_list.append(day_object)

            # restarting counters
            days_to_count -= 1
            total_entries = 0
            start_date_number += 1

        return json.dumps(week_diners_list)

    def get_all_diners(self):
        """
        :rtype: django.db.models.query.QuerySet
        """
        if self.__all_diners is None:
            self.set_all_diners()
        return self.__all_diners

    def set_all_access_logs(self):
        """
        :rtype: django.db.models.query.QuerySet 
        """
        self.__all_access_logs = AccessLog.objects.select_related('diner').order_by('-access_to_room')

    def set_all_diners(self):
        self.__all_diners = Diner.objects.all()


class KitchenHelper(object):
    def __init__(self):
        super(KitchenHelper, self).__init__()
        self.__all_processed_products = None
        self.__all_warehouse = None

    def get_all_processed_products(self):
        """
        :rtype: django.db.models.query.QuerySet 
        """
        if self.__all_processed_products is None:
            self.set_all_processed_products()
        return self.__all_processed_products

    def get_all_warehouse(self):
        """
        :rtype: django.db.models.query.QuerySet 
        """
        if self.__all_warehouse is None:
            self.set_all_processed_products()
        return self.__all_warehouse

    def get_processed_products(self):
        processed_products_list = []
        sales_helper = SalesHelper()
        products_helper = ProductsHelper()

        for processed in self.get_all_processed_products().filter(status='PE')[:15]:
            processed_product_object = {
                'ticket_id': processed.ticket,
                'cartridges': [],
                'packages': [],
                'ticket_order': processed.ticket.order_number
            }

            for ticket_detail in sales_helper.get_all_tickets_details():
                if ticket_detail.ticket == processed.ticket:
                    if ticket_detail.cartridge:
                        cartridge = {
                            'quantity': ticket_detail.quantity,
                            'cartridge': ticket_detail.cartridge,
                        }
                        for extra_ingredient in sales_helper.get_all_extra_ingredients():
                            if extra_ingredient.ticket_detail == ticket_detail:
                                try:
                                    cartridge['name'] += extra_ingredient['extra_ingredient']
                                except Exception as e:
                                    cartridge['name'] = ticket_detail.cartridge.name
                                    cartridge['name'] += ' con ' + extra_ingredient.extra_ingredient.ingredient.name
                        processed_product_object['cartridges'].append(cartridge)

                    elif ticket_detail.package_cartridge:
                        package = {
                            'quantity': ticket_detail.quantity,
                            'package_recipe': []
                        }
                        package_recipe = products_helper.get_all_packages_cartridges_recipes().filter(
                            package_cartridge=ticket_detail.package_cartridge)

                        for recipe in package_recipe:
                            package['package_recipe'].append(recipe.cartridge)
                        processed_product_object['packages'].append(package)

            processed_products_list.append(processed_product_object)
        return processed_products_list

    def set_all_warehouse(self):
        self.__all_warehouse = Warehouse.objects.select_related('supply').all()

    def set_all_processed_products(self):
        self.__all_processed_products = ProcessedProduct.objects. \
            select_related('ticket'). \
            all()
