from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(MyUser, UserAdmin)
admin.site.register(Driver)
admin.site.register(Applicant)
admin.site.register(LoadType)
admin.site.register(Classification)
admin.site.register(Carrier)
admin.site.register(Request)
admin.site.register(Status)
admin.site.register(Trip)
admin.site.register(RequiredClass)
admin.site.register(Message)
admin.site.register(Member)

