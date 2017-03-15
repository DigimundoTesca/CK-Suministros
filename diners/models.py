from django.db import models


class Diner(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	diner_id = models.IntegerField(null=True)
