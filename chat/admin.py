from django.contrib import admin
from .models import ExtendedUser, ChatGroups, ChatMessages, Gallery

admin.site.register([ExtendedUser, ChatGroups, ChatMessages, Gallery],)
# Register your models here.
