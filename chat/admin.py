from django.contrib import admin
from .models import ExtendedUser, ChatGroups, ChatMessages, Gallery, LastSeen

admin.site.register([ExtendedUser, ChatGroups, ChatMessages, Gallery, LastSeen],)
# Register your models here.
