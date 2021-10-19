"""Transport URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.conf.urls import url

from mainApp import consumers
from mainApp.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^signup/', signUp, name='signup'),
    url(r'^login/', signIn, name='login'),
    url(r'^logout/', signOut, name='logout'),
    url(r'^new-request/', newRequest, name='newRequest'),
    url(r'^cancel-request/', cancelRequest, name='cancelRequest'),
    url(r'^add-truck/', newCarrier, name='newCarrier'),
    url(r'^accept-request/', acceptRequest, name='acceptRequest'),
    url(r'^show-request-list/', showRequestList, name='showRequestList'),
    url(r'^chat-driver/', chatDriver, name='chatDriver'),
    url(r'^chat-applicant/', chatApplicant, name='chatApplicant'),
    url(r'^conversation/', conversation, name='conversation'),

]