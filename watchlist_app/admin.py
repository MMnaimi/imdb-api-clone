from django.contrib import admin
from watchlist_app import models


admin.site.register(models.WatchList)
admin.site.register(models.StreamPlatForm)
admin.site.register(models.Review)