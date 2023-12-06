from django.contrib import admin
from .models import AuthenticationMethod, Poll, Choice
admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(AuthenticationMethod)
