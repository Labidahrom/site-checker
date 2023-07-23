from django.contrib import admin
from .models import Url, Check, LastParse


admin.site.register(Url)
admin.site.register(Check)
admin.site.register(LastParse)
