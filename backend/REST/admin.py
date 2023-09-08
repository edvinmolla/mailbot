from django.contrib import admin
from .models import default

@admin.register(default)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ('uemail', 'subject') 