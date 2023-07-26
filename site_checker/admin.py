from django.contrib import admin
from .models import Url, Check, LastParse, TextCheckData


admin.site.register(Url)
admin.site.register(Check)
admin.site.register(LastParse)
admin.site.register(TextCheckData)
