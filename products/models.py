# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.core.validators import MaxValueValidator, MinLengthValidator
from django.db import models

from branchoffices.models import BranchOffice, Supplier


class SuppliesCategory(models.Model):
    name = models.CharField(validators=[MinLengthValidator(4)], max_length=125, unique=True)
    image = models.ImageField(blank=False, upload_to='supplies-categories')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class SupplyLocation(models.Model):
    location = models.CharField(max_length=90, default='')
    branch_office = models.ForeignKey(BranchOffice, default=1, on_delete=models.CASCADE)

    def __str__(self):
        return self.location

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ubicación del Insumo'
        verbose_name_plural = 'Ubicación de los Insumos'


class Supply(models.Model):
    # storage requirement
    DRY_ENVIRONMENT = 'DR'
    REFRIGERATION = 'RE'
    FREEZING = 'FR'
    STORAGE_REQUIREMENTS = (
        (DRY_ENVIRONMENT, 'Ambiente Seco'),
        (REFRIGERATION, 'Refrigeración'),
        (FREEZING, 'Congelación'),
    )

    # optimal duration
    DAYS = 'DA'
    MONTHS = 'MO'
    YEARS = 'YE'
    OPTIMAL_DURATION = (
        (DAYS, 'Dias'),
        (MONTHS, 'Meses'),
        (YEARS, 'Años'),
    )

    # presentation unit
    PACKAGE = 'PA'
    BOX = 'BO'
    PIECE = 'PI'
    PRESENTATION_UNIT = (
        (PACKAGE, 'Paquete'),
        (BOX, 'Caja'),
        (PIECE, 'Pieza')
    )

    # metrics
    GRAM = 'GR'
    MILLILITER = 'MI'
    PIECE = 'PI'

    METRICS = (
        (GRAM, 'gramo'),
        (MILLILITER, 'mililitro'),
        (PIECE, 'pieza'),
    )

    name = models.CharField(validators=[MinLengthValidator(2)], max_length=125, unique=True)
    category = models.ForeignKey(SuppliesCategory, default=1, on_delete=models.CASCADE)
    barcode = models.PositiveIntegerField(
        help_text='(Código de barras de 13 dígitos)',
        validators=[MaxValueValidator(9999999999999)], blank=True, null=True)
    supplier = models.ForeignKey(Supplier, default=1, on_delete=models.CASCADE)
    storage_required = models.CharField(choices=STORAGE_REQUIREMENTS, default=DRY_ENVIRONMENT, max_length=2)
    presentation_unit = models.CharField(max_length=10, choices=PRESENTATION_UNIT, default=PACKAGE)
    presentation_cost = models.FloatField(default=0)
    measurement_quantity = models.FloatField(default=0)
    measurement_unit = models.CharField(max_length=10, choices=METRICS, default=PACKAGE)
    optimal_duration = models.IntegerField(default=0)
    optimal_duration_unit = models.CharField(choices=OPTIMAL_DURATION, max_length=2, default=DAYS)
    location = models.ForeignKey(SupplyLocation, default=1, on_delete=models.CASCADE)
    created_at = models.DateTimeField(editable=False, auto_now=True)
    image = models.ImageField(blank=False, upload_to='supplies')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'


class Cartridge(models.Model):
    # Categories
    FOOD_DISHES = 'FD'
    COMPLEMENTS = 'CO'

    CATEGORIES = (
        (FOOD_DISHES, 'Platillos'),
        (COMPLEMENTS, 'Complementos'),
    )

    name = models.CharField(max_length=128, default='')
    price = models.DecimalField(decimal_places=2, default=0, max_digits=12)
    category = models.CharField(choices=CATEGORIES, default=FOOD_DISHES, max_length=2)
    created_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(blank=False, upload_to='cartridges')

    def __str__(self):
        return self.name

    def get_image(self):
        return """
        <img src="%s" alt="Product image" height="80" >

        """  % self.image.url

    get_image.allow_tags = True
    get_image.short_description = 'Foto'

    class Meta:
        ordering = ('id',)
        verbose_name = 'Cartucho'
        verbose_name_plural = 'Cartuchos'


class CartridgeRecipe(models.Model):
    cartridge = models.ForeignKey(Cartridge, default=1, on_delete=models.CASCADE)
    supply = models.ForeignKey(Supply, default=1, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return '%s' % self.cartridge

    class Meta:
        ordering = ('id',)
        verbose_name = 'Receta del Cartucho'
        verbose_name_plural = 'Recetas de Cartuchos'


class PackageCartridge(models.Model):
    name = models.CharField(max_length=90)
    price = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    package_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def package_recipe(self):
        recipes = PackageCartridgeRecipe.objects.filter(package_cartridge=self.id)
        options = []

        for recipe in recipes:
            options.append(("<option value=%s selected>%s</option>" %
                                (recipe, recipe.cartridge)))
        tag = """<select multiple disabled>%s</select>""" % str(options)
        return tag

    package_recipe.allow_tags = True


    class Meta:
        ordering = ('name',)
        verbose_name = 'Dabba'
        verbose_name_plural = 'Dabbas'


class PackageCartridgeRecipe(models.Model):
    package_cartridge = models.ForeignKey(PackageCartridge, default=1, on_delete=models.CASCADE)
    cartridge = models.ForeignKey(Cartridge, default=1, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return '%s %s' % (self.quantity, self.cartridge)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Receta del Dabba'
        verbose_name_plural = 'Recetas de Dabbas'
