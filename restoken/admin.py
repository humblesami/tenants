from django.contrib import admin
from main_app.admin import BaseAdmin
from restoken.models import PostUserToken


class TokenAdmin(BaseAdmin):
    list_display = ('post_info', 'user', 'token')

admin.site.register(PostUserToken, TokenAdmin)