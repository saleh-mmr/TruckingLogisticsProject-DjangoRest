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
from mainApp.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^usercheck/', isRegistered, name='usercheck'),
    url(r'^check-user-type/', checkUserType, name='checkUserType'),
    url(r'^codecheck/', isValid, name='codecheck'),
    url(r'^signup/', signUp, name='signup'),
    url(r'^signin/', signIn, name='signin'),
    url(r'^signout/', signOut, name='signout'),
    url(r'^get-driver-info/', getDriverInfo, name='getDriverInfo'),
    url(r'^get-class/', getClassifications, name='getClassifications'),
    url(r'^get-numbers/', getNumbers, name='getNumbers'),
    url(r'^get-load/', getLoadType, name='getLoadType'),
    url(r'^new-request/', newRequest, name='newRequest'),
    url(r'^cancel-request/', cancelRequest, name='cancelRequest'),
    url(r'^add-truck/', newCarrier, name='newCarrier'),
    url(r'^show-trucks/', showCarriers, name='showCarriers'),
    url(r'^show-request-list/', showRequestList, name='showRequestList'),
    url(r'^show-request-detail/', showRequestDetail, name='showRequestDetail'),
    url(r'^accept-request/', acceptRequest, name='acceptRequest'),
    url(r'^show-active-trip/', showActiveTrip, name='showActiveTrip'),
    url(r'^show-finished-trip/', showFinishedTrip, name='showFinishedTrip'),
    url(r'^load-announcement/', loadAnnouncement, name='loadAnnouncement'),
    url(r'^unload-announcement/', unloadAnnouncement, name='unloadAnnouncement'),
    url(r'^show-not-accepted-list/', showApplicantRequestList, name='showApplicantRequestList'),
    url(r'^show-accepted-list/', showApplicantTripList, name='showApplicantRequestList'),
    url(r'^show-trip-details/', showApplicantTripDetails, name='showApplicantTripDetails'),
    url(r'^show-applicant-finished-trip-list/', showApplicantFinishedTripList, name='showApplicantFinishedTripList'),

    # url(r'^chat-driver/', chatDriver, name='chatDriver'),
    # url(r'^chat-applicant/', chatApplicant, name='chatApplicant'),
    # url(r'^conversation/', conversation, name='conversation'),
    url(r'^stream-chat', streamChat, name='join'),
]