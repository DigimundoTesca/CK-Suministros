from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# -------------------------------------  Kitchen -------------------------------------
from cloudkitchen.settings.base import PAGE_TITLE
from kitchen.models import ProcessedProduct
from products.models import PackageCartridgeRecipe, Cartridge, PackageCartridge
from sales.models import Ticket, TicketDetail, TicketExtraIngredient


@login_required(login_url='users:login')
def cold_kitchen(request):
    template = 'kitchen/cold.html'
    tickets = Ticket.objects.all()

    def get_processed_products():
        processed_products_list = []
        processed_objects = ProcessedProduct.objects.filter(status='PE')

        for processed in processed_objects:
            processed_product_object = {
                'ticket_id': processed.ticket,
                'cartridges': [],
                'packages': []
            }

            for ticket_detail in TicketDetail.objects.filter(ticket=processed.ticket):
                if ticket_detail.ticket == processed.ticket:
                    if ticket_detail.cartridge:
                        cartridge = {
                            'quantity': ticket_detail.quantity,
                            'cartridge': ticket_detail.cartridge
                        }
                        processed_product_object['cartridges'].append(cartridge)

                    elif ticket_detail.package_cartridge:
                        package = {
                            'quantity': ticket_detail.quantity,
                            'package_recipe': []
                        }
                        package_recipe = \
                            PackageCartridgeRecipe.objects.filter(package_cartridge=ticket_detail.package_cartridge)
                        for recipe in package_recipe:
                            package['package_recipe'].append(recipe.cartridge)
                        processed_product_object['packages'].append(package)

            processed_products_list.append(processed_product_object)
        return processed_products_list

    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'products': get_processed_products(),
        'tickets': tickets,
    }

    return render(request, template, context)


def hot_kitchen(request):
    template = 'kitchen/hot.html'
    tickets = Ticket.objects.all()

    def get_processed_products():
        processed_products_list = []
        processed_objects = ProcessedProduct.objects.filter(status='PE')

        for processed in processed_objects:
            processed_product_object = {
                'ticket_id': processed.ticket,
                'cartridges': [],
                'packages': []
            }

            for ticket_detail in TicketDetail.objects.filter(ticket=processed.ticket):
                if ticket_detail.ticket == processed.ticket:
                    if ticket_detail.cartridge:
                        cartridge = {
                            'quantity': ticket_detail.quantity,
                            'cartridge': ticket_detail.cartridge
                        }
                        processed_product_object['cartridges'].append(cartridge)

                    elif ticket_detail.package_cartridge:
                        package = {
                            'quantity': ticket_detail.quantity,
                            'package_recipe': []
                        }
                        package_recipe = \
                            PackageCartridgeRecipe.objects.filter(package_cartridge=ticket_detail.package_cartridge)
                        for recipe in package_recipe:
                            package['package_recipe'].append(recipe.cartridge)
                        processed_product_object['packages'].append(package)

            processed_products_list.append(processed_product_object)
        return processed_products_list

    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'products': get_processed_products(),
        'tickets': tickets,
    }

    return render(request, template, context)


def kitchen(request):
    template = 'kitchen.html'
    title = 'Cocina'
    tickets = Ticket.objects.all()
    tickets_details = TicketDetail.objects.all()
    extra_ingredients = TicketExtraIngredient.objects.all()
    def get_processed_products():
        processed_products_list = []
        processed_objects = ProcessedProduct.objects.filter(status='PE')

        for processed in processed_objects:
            processed_product_object = {
                'ticket_id': processed.ticket,
                'cartridges': [],
                'packages': [],
                'ticket_order':processed.ticket.order_number
            }

            for ticket_detail in TicketDetail.objects.filter(ticket=processed.ticket):
                if ticket_detail.ticket == processed.ticket:
                    if ticket_detail.cartridge:
                        cartridge = {
                            'quantity': ticket_detail.quantity,
                            'cartridge': ticket_detail.cartridge,
                        }
                        for extra_ingredient in extra_ingredients:
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
                        package_recipe = \
                            PackageCartridgeRecipe.objects.filter(package_cartridge=ticket_detail.package_cartridge)
                        for recipe in package_recipe:
                            package['package_recipe'].append(recipe.cartridge)
                        processed_product_object['packages'].append(package)

            processed_products_list.append(processed_product_object)
        return processed_products_list

    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'extra_ingredients': extra_ingredients,
        'products': get_processed_products(),
        'tickets': tickets,
        'tickets_details': tickets_details,
    }

    return render(request, template, context)


def assembly(request):
    if request.method == 'POST':
        if request.POST['order_id']:
            order = ProcessedProduct.objects.get(ticket=request.POST['order_id'])
            order.status = 'AS'
            order.save()
        return redirect('kitchen:assembly')

    else:
        template = 'assembly.html'
        title = 'Ensamblado'
        
        pending_orders = ProcessedProduct.objects.filter(status='PE')
        orders_list = []

        for order in pending_orders:
            order_object = {
                'ticket_id': order.ticket,
                'ticket_order': order.ticket.order_number,
                'products': [],
                'packages': [],
            }

            ticket_details = TicketDetail.objects.filter(ticket=order.ticket)
            cartridges = Cartridge.objects.all()
            packages = PackageCartridge.objects.all()

            for ticket_detail in ticket_details:
                for cartridge in cartridges:
                    if ticket_detail.cartridge == cartridge:
                        product_object = {
                            'name': ticket_detail.cartridge.name,
                            'quantity': ticket_detail.quantity,
                        }
                        order_object['products'].append(product_object)

                for package in packages:
                    if ticket_detail.package_cartridge == package:
                        package_object = {
                            'name': ticket_detail.package_cartridge.name,
                            'quantity': ticket_detail.quantity,
                        }
                        order_object['packages'].append(package_object)

            orders_list.append(order_object)

        context = {
            'title': PAGE_TITLE + ' | ' + title,
            'page_title': title,
            'title': PAGE_TITLE
        }

        return render(request, template, context)
