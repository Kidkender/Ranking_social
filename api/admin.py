from django.contrib import admin

from .models import Posts, Ranking, Suburbs, Users

admin.site.register(Posts)
admin.site.register(Suburbs)
admin.site.register(Ranking)
admin.site.register(Users)
