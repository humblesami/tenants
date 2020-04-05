from django.contrib import admin

from mainapp.admin import BaseAdmin
from .models import ChatGroup

class ChatGroupForm(BaseAdmin):
    list_display =('name','created_by')


admin.site.register(ChatGroup, ChatGroupForm)