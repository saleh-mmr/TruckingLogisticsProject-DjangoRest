from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import *
from django.contrib.postgres.fields import ArrayField


class MyUser(AbstractUser):
    phone = models.CharField(max_length=50, blank=False, unique=True, default='')
    type = models.BooleanField(blank=False, default=False)


class Driver(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    license_number = models.CharField(blank=False, unique=True, max_length=70)
    can_accept = models.BooleanField(default=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class Applicant(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class LoadType(models.Model):
    title = models.CharField(max_length=70, unique=True)

    def __str__(self):
        return self.title


class Classification(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Carrier(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    classification = models.ForeignKey(Classification, on_delete=models.RESTRICT)
    model = models.CharField(blank=False, max_length=70)
    year = models.IntegerField(blank=False)
    tag = models.CharField(blank=False, max_length=70, unique=True)

    def __str__(self):
        return str(self.model) + ' ' + self.tag


class Request(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    origin = models.CharField(blank=False, max_length=70)
    loading_date = models.DateField(default=date.today)
    destination = models.CharField(blank=False, max_length=70)
    unloading_date = models.DateField(default=date.today)
    load_type = models.ForeignKey(LoadType, on_delete=models.RESTRICT, blank=False, max_length=70)
    weight = models.IntegerField(blank=False)
    value = models.IntegerField(blank=False)
    description = models.CharField(blank=True, max_length=150)
    proposed_price = models.IntegerField(blank=False, default=0)
    receiver_name = models.CharField(blank=False, max_length=70)
    receiver_phone = models.CharField(blank=False, max_length=70)

    def __str__(self):
        return self.applicant.user.username + ' from ' + self.origin + ' to ' + self.destination


class Trip(models.Model):
    request = models.OneToOneField(Request, on_delete=models.RESTRICT)
    carrier = models.ForeignKey(Carrier, on_delete=models.RESTRICT)

    def __str__(self):
        return self.request.origin + ' to ' + self.request.destination + ' by ' + str(self.carrier.model)


class RequiredClass(models.Model):
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.request.id) + ' needs ' + self.classification.title


class Message(models.Model):
    sender = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='receiver')
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='request')
    message = models.CharField(max_length=1200)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
