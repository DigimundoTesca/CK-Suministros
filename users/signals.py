from django.core.signals import request_finished
from django.dispatch import receiver

@receiver(request_finished)
def register_logs(sender,**kwargs):
    print("Probando_ando") 