from django.db import models


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
    diner = models.ForeignKey(Diner, null=True, blank=True)
    RFID = models.CharField(default='', max_length=24)
    access_to_room = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Control de Acceso'
        verbose_name_plural = 'Control de Accesos'

    def __str__(self):
        return self.RFID