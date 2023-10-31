from django.db import models


class Url(models.Model):
    # General
    code = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100, unique=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'django_url'

    def __str__(self):
        return self.name
