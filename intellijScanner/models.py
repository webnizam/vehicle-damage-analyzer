# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings


# Create your models here.

class ExampleModel(models.Model):
    model_pic = models.ImageField(upload_to='static/intellijScanner/', default='static/intellijScanner/None/no-img.jpg')

    def url(self):
        return "{0}{1}".format(settings.MEDIA_URL, self.model_pic.url)

    def name(self):
        return self.model_pic.name
