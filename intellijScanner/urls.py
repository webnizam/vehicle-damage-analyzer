# -*- coding: utf-8 -*-
from django.urls import path
from django.conf.urls import url

from .views import homePageView
from .views import upload_pic

urlpatterns = [
    path('', homePageView, name='home'),
    url(r'^upload_pic/', upload_pic, name='upload_pic'),
]
