from django.contrib import admin
from django.apps import apps

for model in apps.get_app_config("ucath_songs").get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass


admin.site.site_header = 'UCM ADMIN'
admin.site.site_title = 'UCM PORTAL'
admin.site.index_title = 'UCM'