from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),  # главная страница
    path('module/<str:slug>/', GetModule.as_view(), name='module'),
    path('fire/<str:slug>/', GetModuleFire.as_view(), name='fire'),
    path('collection/', Collection.as_view(), name='collection'),
    path('analitics/<str:slug>/<str:methods>/', GetAnalitics.as_view(), name='analitics'),
    path('module/', id_module, name='id_module'),
    path('fire/', id_fire, name='id_fire'),

    path('login/', user_login, name='login'),

    path('logout/', user_logout, name='logout'),

    path('analitics/', id_analitics, name='id_analitics')

]
#    path('container/<str:slug>/', get_container, name='container'),