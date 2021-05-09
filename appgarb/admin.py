from django.contrib import admin
from .models import *

from django import forms


class StreetsAdmin(admin.ModelAdmin):
    list_display = ('id', 's_street')
    list_display_links = ('id', 's_street')
    search_fields = ('s_street',)


class ModulesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"m_slug": ("m_module",)}
    list_display = ('id', 'm_module', 'm_street',  'address',  'm_is_active')
    list_display_links = ('id', 'm_module')
    search_fields = ('m_module',)
    listpython_filter = ('m_street', 'm_is_active')
    readonly_fields = ('m_start',)
    fields = (('m_module', 'm_slug'), 'm_street', 'm_house', 'm_building', 'm_entrance', 'm_height', 'm_cont',
              'm_pipe', 'm_start', 'm_is_active', 'm_method', 'm_params', 'm_plan')
    # save_on_top = True


class ContainersAdmin(admin.ModelAdmin):
    list_display = ('id', 'c_module', 'c_date', 'fill_level', 'c_incr', 'c_is_collected')
    list_display_links = ('id', 'c_module')
    search_fields = ('c_module',)
    list_filter = ('c_module', 'c_date',)
   # readonly_fields = ('c_module', 'c_date', 'c_curr')
    fields = ('c_module', 'c_date', 'c_curr', 'c_incr', 'c_is_collected')


class FireAdmin(admin.ModelAdmin):
    list_display = ('id', 'f_module', 'f_alarm', 'f_temp', 'f_smoke')
    list_display_links = ('id', 'f_module')
    search_fields = ('f_module',)
    list_filter = ('f_module', )
   # readonly_fields = ('f_module','f_alarm', 'f_temp', 'f_smoke')
    fields = ('f_module', 'f_alarm', 'f_temp', 'f_smoke')

class AnaliticsAdmin(admin.ModelAdmin):
    list_display = ('id', 'a_module', 'date_collection', 'a_period', 'a_fullness', 'incr_average')
    list_display_links = ('id', 'a_module')
    search_fields = ('a_module',)
    list_filter = ('a_module', 'a_date',)
   # readonly_fields = ('a_module', 'a_date', 'a_period',)
    fields = ('a_module', 'a_date', 'a_period', 'a_fullness')

class MethodsAdmin(admin.ModelAdmin):
    list_display = ('id', 'me_method')
    list_display_links = ('id', 'me_method')
    search_fields = ('me_methods',)

admin.site.register(Streets, StreetsAdmin)  # порядок параметров важен
admin.site.register(Modules, ModulesAdmin)
admin.site.register(Containers, ContainersAdmin)
admin.site.register(Fire, FireAdmin)
admin.site.register(Analitics, AnaliticsAdmin)
admin.site.register(Methods, MethodsAdmin)
