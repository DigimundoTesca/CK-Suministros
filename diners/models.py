from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone


class Diner(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=160, default='')
    employee_number = models.CharField(max_length=32, default='', unique=True)
    RFID = models.CharField(default='', max_length=24, unique=True)

    class Meta:
        verbose_name = 'Comensal'
        verbose_name_plural = 'Comensales'

    def __str__(self):
        return self.name


class AccessLog(models.Model):
    diner = models.ForeignKey(Diner, null=True, blank=True, on_delete=models.CASCADE)
    RFID = models.CharField(default='', max_length=24)
    access_to_room = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Control de Acceso'
        verbose_name_plural = 'Control de Accesos'

    def __str__(self):
        return self.RFID


class ElementToEvaluate(models.Model):
    element = models.CharField(max_length=48, default='', unique=True)
    priority = models.IntegerField(default=1)
    permanent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    publication_date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = "Elemento a evaluar"
        verbose_name_plural = "Elementos a evaluar"

    def __str__(self):
        return self.element


class SatisfactionRating(models.Model):
    elements = models.ManyToManyField(ElementToEvaluate)
    satisfaction_rating = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(4)])
    creation_date = models.DateTimeField(auto_now_add=True)
    suggestion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Índice de Satisfacción"
        verbose_name_plural = "Índices de Satisfacción"

    def __str__(self):
        return '%s' % self.satisfaction_rating

    def shortened_suggestion(self):
        text = str(self.suggestion)
        text = (text[:48] + '...') if len(text) > 12 else text
        return text
