
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth.decorators import login_required

from branchoffices.models import Supplier
from cloudkitchen.settings.base import PAGE_TITLE
from products.forms import SupplyForm, SuppliesCategoryForm, CartridgeForm
from products.models import Cartridge, Supply, SuppliesCategory
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import CreateView

class Create_Supply(CreateView):
    model = Supply
    fields = ['name','category','barcode','supplier','storage_required','presentation_unit','presentation_cost',
        'measurement_quantity','measurement_unit','optimal_duration','optimal_duration_unit','location','image']
    template_name = 'new_supply.html'   

    def form_valid(self,form):
        self.object = form.save()        
        return redirect('/supplies/')

class Update_Supply(UpdateView):
    model = Supply
    fields = ['name','category','barcode','supplier','storage_required','presentation_unit','presentation_cost',
        'measurement_quantity','measurement_unit','optimal_duration','optimal_duration_unit','location','image']
    template_name = 'new_supply.html'

    def form_valid(self,form):
        self.object = form.save()
        return redirect('/supplies/')

class Delete_Supply(DeleteView):
    model = Supply
    template_name = 'delete_supply.html'

    def delete(self, request, *args, **kwargs):        
        self.object = self.get_object()        
        self.object.delete()
        return redirect('/supplies/')

class Create_Cartridge(CreateView):
    model = Cartridge
    fields = ['name','price','category','image']
    template_name = 'new_cartridge.html'     

    def form_valid(self,form):
        self.object = form.save()
        return redirect('/cartridges/')

class Update_Cartridge(UpdateView):
    model = Cartridge
    fields = ['name','price','category','image']
    template_name = 'new_cartridge.html'

    def form_valid(self,form):
        self.object = form.save()
        return redirect('/cartridges/')

class Delete_Cartridge(DeleteView):
    model = Cartridge
    template_name = 'delete_cartridge.html'

    def delete(self, request, *args, **kwargs):        
        self.object = self.get_object()        
        self.object.delete()
        return redirect('/cartridges/')

def test(request):
    # template = 'base/base_nav_footer.html'
    template = 'base/nav.html'
    return render(request, template, {})


# -------------------------------------  Profile -------------------------------------


# -------------------------------------  Providers -------------------------------------
@login_required(login_url='users:login')
def suppliers(request):
    suppliers_list = Supplier.objects.order_by('id')
    template = 'suppliers/suppliers.html'
    title = 'Proveedores'
    context = {
        'suppliers': suppliers_list,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


# -------------------------------------  Supplies -------------------------------------
@login_required(login_url='users:login')
def supplies(request):
    supplies_objects = Supply.objects.order_by('id')
    template = 'supplies/supplies.html'
    title = 'Insumos'
    context = {
        'supplies': supplies_objects,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def new_supply(request):
    if request.method == 'POST':
        form = SupplyForm(request.POST, request.FILES)
        if form.is_valid():
            supply = form.save(commit=False)
            supply.save()
            return redirect('/supplies/')
    else:
        form = SupplyForm()

    template = 'supplies/new_supply.html'
    title = 'DabbaNet - Nuevo insumo'
    categories_list = SuppliesCategory.objects.order_by('name')
    suppliers_list = Supplier.objects.order_by('name')
    context = {
        'categories': categories_list,
        'suppliers': suppliers_list,
        'form': form,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def supply_detail(request, pk):
    supply = get_object_or_404(Supply, pk=pk)
    template = 'supplies/supply_detail.html'
    title = 'DabbaNet - Detalles del insumo'
    context = {
        'page_title': PAGE_TITLE,
        'supply': supply,
        'title': title
    }
    return render(request, template, context)

@login_required(login_url='users:login')
def supply_modify(request,pk):
    supply = get_object_or_404(Supply, pk=pk) 

    if request.method == 'POST':        
        form = SupplyForm(request.POST, request.FILES)

        if form.is_valid():
            nuevo = form.save(commit=False)
            supply.name = nuevo.name
            supply.category = nuevo.category
            supply.barcode = nuevo.barcode
            supply.supplier = nuevo.suppliter
            supply.storage_required = nuevo.storage_required
            supply.presentation_unit = nuevo.presentation_unit
            supply.presentation_cost = nuevo.presentation_cost
            supply.measurement_quantity = nuevo.measurement_quantity
            supply.measurement_unit = nuevo.measurement_unit
            supply.optimal_duration = nuevo.optimal_duration
            supply.optimal_duration_unit = nuevo.optimal_duration_unit
            supply.location = nuevo.location
            supply.image = nuevo.image            
            supply.save()

            return redirect('/supply')        
            
    else:
        dic = {
            'name' : supply.name,           
            'category' : supply.category ,
            'barcode' : supply.barcode,
            'supplier' : supply.supplier,
            'storage_required' : supply.storage_required,
            'presentation_unit' : supply.presentation_unit,
            'presentation_cost' : supply.presentation_cost,
            'quantity' : supply.measurement_quantity,
            'measurement_unit' : supply.measurement_unit,
            'optimal_duration' : supply.optimal_duration,
            'optimal_duration_unit' : supply.optimal_duration_unit,
            'location' : supply.location,
            'image' : supply.image,    
        }
        form = SupplyForm(initial=dic)

    template = 'supplies/new_supply.html'
    title = 'Modificar Insumo'
    context = {
        'form': form,
        'supply' : supply,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)

# ------------------------------------- Categories -------------------------------------
@login_required(login_url='users:login')
def categories(request):
    supplies_categories = SuppliesCategory.objects.order_by('id')
    template = 'categories/categories.html'
    title = 'Categorias'
    context = {
        'supplies_categories': supplies_categories,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def new_category(request):
    if request.method == 'POST':
        form = SuppliesCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect('/categories')
    else:
        form = SuppliesCategoryForm()

    template = 'categories/new_category.html'
    title = 'Nueva Categoria'
    context = {
        'form': form,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def categories_supplies(request, categ):
    supplies_categories = SuppliesCategoryForm.objects.filter(name=categ)
    supply = Supply.objects.filter(category=supplies_categories)
    template = 'supplies/supplies.html'
    title = categ
    context = {
        'supply': supply,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


# -------------------------------------  Cartridges -------------------------------------
@login_required(login_url='users:login')
def cartridges(request):
    cartridges_list = Cartridge.objects.order_by('id')
    template = 'cartridges/cartridges.html'
    title = 'Cartuchos'
    context = {
        'cartridges': cartridges_list,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def new_cartridge(request):
    if request.method == 'POST':
        form = CartridgeForm(request.POST, request.FILES)
        if form.is_valid():
            cartridge = form.save(commit=False)
            cartridge.save()
            return redirect('/cartridges')
    else:
        form = CartridgeForm()

    template = 'cartridges/new_cartridge.html'
    title = 'Nuevo Cartucho'
    context = {
        'form': form,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def cartridge_detail(request, pk):
    cartridge = get_object_or_404(Cartridge, pk=pk)
    template = 'cartridges/cartridge_detail.html'
    title = 'DabbaNet - Detalles del Producto'
    context = {
        'page_title': PAGE_TITLE,
        'cartridge': cartridge,
        'title': title
    }
    return render(request, template, context)

def cartridge_modify(request, pk):
    cartridge = get_object_or_404(Cartridge, pk=pk)      

    if request.method == 'POST':
        form = CartridgeForm(request.POST, request.FILES)  

        if form.is_valid():
            nuevo = form.save(commit=False)
            cartridge.name = nuevo.name
            cartridge.price = nuevo.price
            cartridge.category = nuevo.category
            cartridge.save()
            return redirect('/cartridges')        
            
    else:
        dic = {
            'name' : cartridge.name, 
            'price' : cartridge.price,
            'category' : cartridge.category,
            'image' : cartridge.image
        }
        form = CartridgeForm(initial=dic)

    template = 'cartridges/new_cartridge.html'
    title = 'Modificar Cartucho'
    context = {
        'form': form,
        'cartridge' : cartridge,
        'title': title,
        'page_title': PAGE_TITLE
    }
    return render(request, template, context)
