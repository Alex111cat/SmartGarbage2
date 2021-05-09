from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views.generic import ListView, DetailView
from .models import *
from .forms import ModuleForm, AnaliticsForm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from math import sqrt
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import statsmodels.api as sm
import os, json, time, ast, datetime
from django.http import HttpResponseRedirect
from .utils import MyMixin
from django.db.models import Max
import warnings, itertools

class Home(MyMixin, ListView):
    template_name = 'appgarb/index.html'
    context_object_name = 'containers'

    def get_context_data(self, *, object_list=None, **kwargs):
        # queryset = object_list
        # if object_list is not None else self.object_list
        context = super().get_context_data(**kwargs)
        context['title'] = 'Таблица'
        context['date'] = self.get_today()
        return context

    def get_queryset(self):
        if self.get_today():  # если есть хоть одна запись в бд
            modules = Modules.objects.filter(m_is_active=True)
            for item in modules:
                try:
                    # если имеется показание за текущуую дату
                    c_obj = Containers.objects.filter(c_date=self.get_today(), c_is_collected=False).get(
                        c_module__m_module=item.m_module)

                    # заполнение поля суточного прироста, если оно пусто
                    if (c_obj.c_incr == None):
                        if (c_obj.fill_level != 0):
                            try:
                                c_obj_prev = c_obj.get_previous_by_c_date(c_module__m_module=item.m_module,
                                                                          c_curr__isnull=False)
                                if (c_obj_prev.fill_level <= c_obj.fill_level):
                                    c_obj.c_incr = c_obj.fill_level - c_obj_prev.fill_level
                                else:
                                    c_obj.c_incr = 0  # если предыдущий уровень мусора выше текущего
                            except Containers.DoesNotExist:
                                c_obj.c_incr = 0  # для первой записи модуля
                        else:
                            try:
                                c_obj_prev = c_obj.get_previous_by_c_date(c_module__m_module=item.m_module)
                                if (c_obj_prev.fill_level == 0):
                                    c_obj.c_incr = 0
                            except Containers.DoesNotExist:
                                pass
                        c_obj.save(update_fields=["c_incr"])
                except Containers.DoesNotExist:
                    module = Modules.objects.get(m_module=item)
                    # # если показание за текущую дату не пришло
                    module.containers_set.create(c_module=item.m_module, c_date=self.get_today(), c_incr=0)
            queryset = Containers.objects.filter(c_date=self.get_today(), c_is_collected=False)
            for item in queryset:
                obj_fire = Fire.objects.filter(f_module__m_module=item.c_module, f_alarm=self.get_today())
                # if obj_fire:
                #     item.fire = 'Пожарная тревога!'

                if (str(item.c_module) == '0001'):
                    item.fire = 'Пожарная тревога!'
        else:
            queryset = Containers.objects.all()
        return queryset

    def post(self, request, *args, **kwargs):
        if request.POST.get("calculate"):  # запрос пришел от кнопки
            modules = Modules.objects.filter(m_is_active=True)
            for item in modules:
                self.get_pred(item)
        return HttpResponseRedirect("/")

class GetModule(MyMixin, DetailView):
    template_name = 'appgarb/module.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('period'):
                s_list = (request.GET.get('start')).split('/')
                s_date = datetime.datetime(int(s_list[2]), int(s_list[1]), int(s_list[0]))
                start_date = datetime.datetime.date(s_date)
                e_list = (request.GET.get('end')).split('/')
                e_date = datetime.datetime(int(e_list[2]), int(e_list[1]), int(e_list[0]))
                end_date = datetime.datetime.date(e_date)
                s1_list = (request.GET.get('start1')).split('/')
                s1_date = datetime.datetime(int(s1_list[2]), int(s1_list[1]), int(s1_list[0]))
                start1_date = datetime.datetime.date(s1_date)
                e1_list = (request.GET.get('end1')).split('/')
                e1_date = datetime.datetime(int(e1_list[2]), int(e1_list[1]), int(e1_list[0]))
                end1_date = datetime.datetime.date(e1_date)
        else:
            end_date = end1_date = self.get_today().date()
            start_date = end_date - datetime.timedelta(days=14)
            start1_date = end_date - datetime.timedelta(days=100)
        request.GET = {}
        list = [start_date, start1_date, end_date, end1_date]
        context = self.get_context_data(object_list=list)
        context['module_item'] = self.get_object()
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        if self.kwargs['slug']:
            slug = self.kwargs['slug']
            obj = Modules.objects.get(m_module=slug)
            if obj.m_is_active:
                try:
                    obj = Containers.objects.get(c_module__m_module=slug, c_date=self.get_today(), c_is_collected=False)
                    obj_fire= Fire.objects.filter(f_module__m_module=slug, f_alarm=self.get_today())
                    # if obj_fire:
                    if obj:
                        obj.fire = 'Пожарная тревога!'
                    obj.no_curr = 'Нет показаний'
                    obj.no_active = None
                except Containers.DoesNotExist:
                    pass
            else:
                obj.no_active = 'Модуль неактивен'
                obj.no_curr = 'Нет показаний'
        else:
            obj = None
        return obj

    def get_context_data(self, *, object_list, **kwargs):
        context = {}
        # context = super().get_context_data(**kwargs)
        start_date = object_list[0]
        start1_date = object_list[1]
        end_date = object_list[2]
        end1_date = object_list[3]
        slug = self.kwargs['slug']
        context['is_chosen'] = True
        context['title'] = 'Мониторинг'
        context['start_date'] = start_date
        context['start1_date'] = start1_date
        context['end_date'] = end_date
        context['end1_date'] = end1_date
        start_dt = datetime.datetime.combine(start_date, datetime.time(6, 0, 0))
        start_dt1 = datetime.datetime.combine(start1_date, datetime.time(6, 0, 0))
        end_dt = datetime.datetime.combine(end_date, datetime.time(6, 0, 0))
        end_dt1 = datetime.datetime.combine(end1_date, datetime.time(6, 0, 0))
        # линейный график
        data, labels = [], []
        try:
            queryset = Containers.objects.filter(c_module__m_module=slug, c_date__gte=start_dt,
                                                 c_date__lte=end_dt).exclude(c_curr=None)
            for item in queryset:
                c_d = item.c_date
                c_date_for_js = int(time.mktime(c_d.timetuple())) * 1000  # перевод в миллисекунды для js
                labels.append(c_date_for_js)
                data.append(item.fill_level)
        except Containers.DoesNotExist:
            pass
        context['labels'] = labels
        context['data'] = data
        # диаграмма
        data1, labels1, fullness = [], [], []
        try:
            queryset = Analitics.objects.filter(a_module__m_module=slug, a_date__gte=start_dt1, a_date__lte=end_dt1)
            for item in queryset:
                a_d = item.a_date
                a_date_for_js = int(time.mktime(a_d.timetuple())) * 1000  # перевод в миллисекунды для js
                labels1.append(a_date_for_js)
                data1.append(item.a_period)
                fullness.append(item.a_fullness)
        except Analitics.DoesNotExist:
            pass
        context['labels1'] = labels1
        context['data1'] = data1
        context['fullness'] = fullness
        return context

def id_module(request):
    title = 'Мониторинг'
    if request.method == 'POST':
        form = ModuleForm(request.POST or None)
        if form.is_valid():
            return redirect('module', form.cleaned_data.get('module'))
    else:
        form = ModuleForm()
    return render(request, 'appgarb/module.html', {'form': form, 'title': title})

class GetModuleFire(MyMixin, DetailView):
    template_name = 'appgarb/fire.html'
    context_object_name = 'fire_item'

    def get_object(self, queryset=None):
        if self.kwargs['slug']:
            slug = self.kwargs['slug']
            obj = Modules.objects.get(m_module=slug)
            obj.temp = "В пределах нормы"
            obj.smoke = "Отсутствует"
            start = datetime.datetime.now() - datetime.timedelta(hours = 3)


            # if obj.m_is_active:
            #     obj_fire_temp = Fire.objects.filter(f_module__m_module=slug, f_alarm__gte=start,
            #                                    f_alarm__lte=datetime.datetime.now(), f_temp__isnull=False)
            #     obj_fire_smoke = Fire.objects.filter(f_module__m_module=slug, f_alarm__gte=start,
            #                                         f_alarm__lte=datetime.datetime.now(), f_smoke__isnull=False)
            #     labels_temp, labels_smoke = [], []
            #     data_temp, data_smoke = [], []
            #     obj.date_fire = None
            #     if obj_fire_temp or obj_fire_smoke:
            #         obj.fire = 'Пожарная тревога!'
            #     if obj_fire_temp:
            #         obj.date_fire = obj_fire_temp.last().f_alarm
            #         obj.temp = obj_fire_temp.last().f_temp
            #         for item in obj_fire_temp:
            #             f_d = item.f_alarm
            #             f_date_for_js = int(time.mktime(f_d.timetuple())) * 1000  # перевод в миллисекунды для js
            #             labels_temp.append(f_date_for_js)
            #             data_temp.append(item.f_temp)
            #         obj.labels_temp = labels_temp
            #         obj.data_temp = data_temp
            #     if obj_fire_smoke:
            #         date_smoke = obj_fire_smoke.last().f_alarm
            #         if obj.date_fire:
            #             if obj.date_fire < date_smoke:
            #                 obj.date_fire = date_smoke
            #         else:
            #            obj.date_fire = date_smoke
            #         obj.temp = obj_fire_smoke.last().f_smoke
            #         for item in obj_fire_smoke:
            #             f_d = item.f_alarm
            #             f_date_for_js = int(time.mktime(f_d.timetuple())) * 1000  # перевод в миллисекунды для js
            #             labels_smoke.append(f_date_for_js)
            #             data_smoke.append(item.f_smoke)
            #         obj.labels_smoke = labels_smoke
            #         obj.data_smoke = data_smoke
            #     obj.no_active = None
            # else:
            #     obj.no_active = 'Модуль неактивен'



        else:
            obj = None
        return obj

    def get_context_data(self, *, object_list: object = None, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['is_chosen'] = True
        context['title'] = 'Пожарная тревога'
        labels2 = []
        for i in range(0, 6):
            for j in range(0, 2):
                lab = datetime.datetime.combine(self.get_today().date(), datetime.time(6, 0 + i, j * 30))
                labels2.append(int(time.mktime(lab.timetuple())) * 1000)
        data_temp = [36, 38, 39, 41, 45, 43, 45, 42, 47, 49, 47, 50]
        data_smoke = [35, 38, 37, 36, 37, 38, 40, 39, 37, 40, 39, 40]
        context['date_fire'] = lab
        context['temp'] = data_temp[-1]
        context['smoke'] = data_smoke[-1]
        context['labels2'] = labels2
        context['data_temp'] = data_temp
        context['data_smoke'] = data_smoke
        return context

def id_fire(request):
    title = 'Пожарная тревога'
    if request.method == 'POST':
        form = ModuleForm(request.POST or None)
        if form.is_valid():
            return redirect('fire', form.cleaned_data.get('module'))
    else:
        form = ModuleForm()
    return render(request, 'appgarb/fire.html', {'form': form, 'title': title})

class Collection(MyMixin, ListView):
    template_name = 'appgarb/collection.html'
    context_object_name = 'containers'

    def get(self, request, *args, **kwargs):
        context = {}
        if request.GET.get("collect"):  # запрос пришел от кнопки
            check_values = request.GET.getlist('item')  # какие модули отмечены галочками
            queryset = Containers.objects.filter(c_module__m_module__in=check_values,
                                                 c_date=self.get_today(), c_is_collected=False)
        else:  # запрос пришел от нажатия sidebar
            if self.get_today():
                queryset = Containers.objects.filter(c_date=self.get_today(), c_is_collected=False)
                for item in queryset:
                    if not (Containers.get_fill(item) >= 100):
                        queryset = queryset.exclude(pk=item.pk)
        context['title'] = 'Путевой лист'
        context['date'] = now()
        context['get_request'] = True
        context[self.context_object_name] = queryset
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        context = {}
        if request.POST.get("confirm"):  # запрос пришел от кнопки
            check_values = request.POST.getlist('item')
            queryset = Containers.objects.filter(c_module__m_module__in=check_values, c_date=self.get_today(),
                                                 c_is_collected=False)
            for item in queryset:
                item.is_collected = 'Вывезено'
            for item in check_values:
                try:  # если мусор уже вывезен - ничего не делаем
                    obj_c = Containers.objects.get(c_module__m_module=item, c_date=self.get_today(), c_is_collected=True)
                except Containers.DoesNotExist:  # если мусор еще не вывезен
                    module = Modules.objects.get(m_module=item)
                    obj_c = Containers.objects.get(c_module__m_module=item, c_date=self.get_today(), c_is_collected=False)
                    # корректировка и добавление
                    obj_c.c_is_collected = True
                    obj_c.save()
                    try:
                        obj_c = Containers.objects.get(c_module__m_module=item, c_date=self.get_today(),
                                                       c_is_collected=False)
                        obj_c.delete()  # удаляем чтобы не было дублирования при повторном запуске подтверждения вывоза
                    except Containers.DoesNotExist:
                        pass
                    module.containers_set.create(c_module=module.m_module, c_date=self.get_today(),
                                                 c_curr=module.m_height, c_is_collected=False, c_incr=None)
                    self.get_pred(module) # расчет плановой даты
                    try:
                        obj_a = Analitics.objects.get(a_module__m_module=item, a_date=self.get_today().date())  # перезапись костыль
                        obj_a.delete()
                    except Analitics.DoesNotExist:
                        pass
                    try:
                        object_last = Analitics.objects.filter(a_module__m_module=item).latest('a_date')
                        period = self.get_today().date() - object_last.a_date.date()
                        # object_last.a_date - последний день вывоза мусора по данному модулю
                    except Analitics.DoesNotExist:
                        period = self.get_today().date() - module.m_start
                    #     нельзя добавлять напрямую из-за ForeignKey
                    if (obj_c.fill_level == None):  # усли вывозится контейнер с неопределившимся показанием, берем предшествующее
                        try:
                            obj_c_prev = obj_c.get_previous_by_c_date(c_module__m_module=module.m_module,
                                                                      c_curr__isnull=False)
                            fill = obj_c_prev.fill_level
                        except Containers.DoesNotExist:
                            fill = 0
                    else:
                        fill = obj_c.fill_level
                    module.analitics_set.create(a_module=module.m_module, a_date=self.get_today().date(),
                                                a_period=period.days, a_fullness=fill)
        context['title'] = 'Путевой лист'
        context['date'] = now()
        context['get_request'] = False
        context[self.context_object_name] = queryset
        return render(request, template_name=self.template_name, context=context)

def id_analitics(request):
    title = 'Аналитика'
    if request.method == 'POST':
        form = AnaliticsForm(request.POST or None)
        if form.is_valid():
            module = form.cleaned_data.get('module')
            methods = form.cleaned_data.get('methods')
            list = []
            for item in methods:
                list.append(str(item))
            methods = '+'.join(list)
            return redirect('analitics', module, methods)
    else:
        form = AnaliticsForm()
    return render(request, 'appgarb/analitics.html', {'form': form, 'title': title})

class GetAnalitics(MyMixin, DetailView):
    template_name = 'appgarb/analitics.html'
    context_object_name = 'analitics_item'

    def get_object(self, queryset=None):
        for i in os.listdir('media'):
            os.remove('media' + '/' + i)
        warnings.filterwarnings("ignore")  # отключает предупреждения
        methods = self.kwargs['methods']
        methods = methods.split('+')
        if self.kwargs['slug']:
            slug = self.kwargs['slug']
            try:
                obj = Modules.objects.get(m_module=slug)
                obj.no_active = None
                if obj.m_is_active == False:
                    obj.no_active = "Модуль неактивен"
                else:
                    rms_arr, data_pred, labels_pred, pars = [], [], [], []
                    try:
                        queryset = Containers.objects.filter(c_module__m_module=slug, c_incr__isnull=False)
                        for item in queryset:
                            labels_pred.append(item.c_date.date())
                            data_pred.append(item.c_incr)
                        dd = np.asarray(data_pred)
                        df = pd.DataFrame(data=dd, index=pd.to_datetime(labels_pred), columns=['value'])
                        max_period = Analitics.objects.filter(a_module__m_module=obj.m_module).aggregate(Max('a_period'))
                        forecast_period = int(max_period['a_period__max'])
                        train = df[0:-forecast_period]
                        test = df[-forecast_period:]
                        # df = df.resample('D').mean()
                        # train = train.resample('D').mean()
                        # test = test.resample('D').mean()
                        y_hat_avg = test.copy()
                        plt.rcParams.update({'font.size': 14})
                        # проверка на стационарность
                        analiz, d_7 = self.stationarity(train.value)
                        for item in methods:
                            start = time.time()
                            rms = 1000000000.0
                        # ===================================================================================
                            if item == 'Наивный подход':
                                y_hat_avg['naive'] = dd[len(train) - 1]
                                # Расчет среднеквадратичной ошибки (RMSE)
                                rms = sqrt(mean_squared_error(test.value, y_hat_avg.naive))
                                duration = time.time() - start
                                plt.figure(figsize=(16, 10))
                                plt.plot(train.index, train['value'], label='Train')
                                plt.plot(test.index, test['value'], label='Test')
                                plt.plot(y_hat_avg.index, y_hat_avg['naive'], label='Naive Forecast')
                                plt.legend(loc='best')
                                plt.title("Naive Forecast \n (RMSE = " + str(round(rms, 10)) + ", time = " + str(
                                    round(duration, 3)) + "c)", fontsize=35, fontweight='bold')
                                plt.savefig('media/naive_forecast.png')
                                pars.append(None)
                            # ===================================================================================
                            elif item == 'Простое среднее':
                                y_hat_avg['avg_forecast'] = train['value'].mean()
                                duration = time.time() - start
                                plt.figure(figsize=(16, 10))
                                plt.plot(train.index, train['value'], label='Train')
                                plt.plot(test.index, test['value'], label='Test')
                                plt.plot(y_hat_avg['avg_forecast'], label='Average Forecast')
                                plt.legend(loc='best')
                                rms = sqrt(mean_squared_error(test.value, y_hat_avg.avg_forecast))
                                plt.title("Average Forecast \n (RMSE = " + str(round(rms, 10)) + ", time = " + str(
                                    round(duration, 3)) + "c)", fontsize=35, fontweight='bold')
                                plt.savefig('media/average_forecast.png')
                                pars.append(None)
                            # ===================================================================================
                            elif item == 'Скользящее среднее':
                                y_hat_avg['moving_avg_forecast'] = train['value'].rolling(48).mean().iloc[-1]
                                rms = sqrt(mean_squared_error(test.value, y_hat_avg.moving_avg_forecast))
                                duration = time.time() - start
                                plt.figure(figsize=(16, 10))
                                plt.plot(train.index, train['value'], label='Train')
                                plt.plot(test.index, test['value'], label='Test')
                                plt.plot(y_hat_avg['moving_avg_forecast'], label='Moving Average Forecast')
                                plt.legend(loc='best')
                                plt.title("Moving Average Forecast \n  (RMSE = " + str(round(rms, 10)) + ", time = " + str(
                                    round(duration, 3)) + "c)", fontsize=35, fontweight='bold')
                                plt.savefig('media/mov_avg_forecast.png')
                                pars.append(None)
                            # ===================================================================================
                            elif item == 'Простое экспоненциальное сглаживание':
                                for s_l in np.arange(0, 1, 0.1):
                                    fit2_curr = SimpleExpSmoothing(np.asarray(train['value'])).fit(smoothing_level=s_l,
                                                                                                   optimized=False)
                                    y_hat_avg['SES'] = fit2_curr.forecast(len(test))
                                    rms_curr = sqrt(mean_squared_error(test.value, y_hat_avg.SES))
                                    if (rms_curr < rms):
                                        rms = rms_curr
                                        plt.plot(y_hat_avg['SES'], label='SES')
                                        fit2 = fit2_curr
                                        p4 = {'s_l': round(s_l, 4)}
                                y_hat_avg['SES'] = fit2.forecast(len(test))
                                duration = time.time() - start
                                plt.figure(figsize=(16, 10))
                                plt.plot(train.index, train['value'], label='Train')
                                plt.plot(test.index, test['value'], label='Test')
                                plt.plot(y_hat_avg['SES'], label='SES')
                                plt.legend(loc='best')
                                plt.title("Simple Exponential Smoothing  \n (RMSE = " + str(round(rms, 10)) + ", time = " + str(
                                    round(duration, 3)) + "c)", fontsize=35, fontweight='bold')
                                plt.savefig('media/ses.png')
                                pars.append(p4)
                            # ===================================================================================
                            elif item == 'Метод линейного тренда Холта':
                                for s_l in np.arange(0, 1, 0.1):
                                    for s_s in np.arange(0, 1, 0.1):
                                        fit1_curr = Holt(np.asarray(train['value'])).fit(smoothing_level=s_l,
                                                                                         smoothing_trend=s_s)
                                        y_hat_avg['Holt_linear'] = fit1_curr.forecast(len(test))
                                        rms_curr = sqrt(mean_squared_error(test.value, y_hat_avg.Holt_linear))
                                        if (rms_curr < rms):
                                            rms = rms_curr
                                            fit1 = fit1_curr
                                            p5 = {'s_l': round(s_l, 4), 's_s': round(s_s, 4)}
                                duration = time.time() - start
                                y_hat_avg['Holt_linear'] = fit1.forecast(len(test))
                                plt.figure(figsize=(16, 10))
                                plt.plot(train.index, train['value'], label='Train')
                                plt.plot(test.index, test['value'], label='Test')
                                plt.plot(y_hat_avg['Holt_linear'], label='Holt_linear')
                                plt.legend(loc='best')
                                plt.title("Holt linear trend method \n  (RMSE = " + str(round(rms, 10)) + ", time = " + str(
                                    round(duration, 3)) + "c)", fontsize=35, fontweight='bold')
                                plt.savefig('media/holt_linear.png')
                                pars.append(p5)
                            # ===================================================================================
                            elif item == 'Метод Холта-Винтерса':
                                params = ['add', None]
                                for t in params:
                                    for s in params:
                                        for s_p in [7, 12]:
                                            try:
                                                fit1_curr = ExponentialSmoothing(np.asarray(train['value']),
                                                                                 seasonal_periods=s_p, trend=t, seasonal=s, ).fit()
                                                y_hat_avg['Holt_Winter'] = fit1_curr.forecast(len(test))
                                                rms_curr = sqrt(mean_squared_error(test.value, y_hat_avg.Holt_Winter))
                                                if (rms_curr < rms):
                                                    rms = rms_curr
                                                    fit1 = fit1_curr
                                                    p6 = {'s_p': s_p, 't': t, 's': s}
                                            except:
                                                pass
                                duration = time.time() - start
                                y_hat_avg['Holt_Winter'] = fit1.forecast(len(test))
                                plt.figure(figsize=(16, 10))
                                plt.plot(train.index, train['value'], label='Train')
                                plt.plot(test.index, test['value'], label='Test')
                                plt.plot(y_hat_avg['Holt_Winter'], label='Holt_Winter')
                                plt.legend(loc='best')
                                plt.title(" Holt-Winters method \n (RMSE = " + str(round(rms, 10)) + ", time = " + str(
                                    round(duration, 3)) + "c)", fontsize=35, fontweight='bold')
                                plt.savefig('media/holt_winter.png')
                                pars.append(p6)
                            # ===================================================================================
                            elif item == 'SARIMA':
                                y_hat_avg = test.copy()
                                p = q = range(0, 4)
                                D = range(0, 2)
                                m = [7, 12]
                                pdq = list(itertools.product(p, d_7, q))
                                seasonal_pdq = [(x[0], x[1], x[2], x[3]) for x in list(itertools.product(p, D, q, m))]
                                for param in pdq:
                                    for param_seasonal in seasonal_pdq:
                                        try:
                                            fit1_curr = sm.tsa.statespace.SARIMAX(train.value, order=param,
                                                                                  seasonal_order=param_seasonal, enforce_stationarity=False,
                                                                                  enforce_invertibility=False).fit()
                                            y_hat_avg['SARIMA'] = fit1_curr.predict(start=test.index[0].date(),
                                                                                    end=self.get_today().date(), dynamic=True)
                                            rms_curr = sqrt(mean_squared_error(test.value, y_hat_avg.SARIMA))
                                            if (rms_curr < rms):
                                                rms = rms_curr
                                                fit1 = fit1_curr
                                                p7 = {'p': param[0], 'd': param[1], 'q': param[2],
                                                      'P': param_seasonal[0], 'D': param_seasonal[1], 'Q': param_seasonal[2], 'm': param_seasonal[3]}
                                        except:
                                            pass
                                duration = time.time() - start
                                y_hat_avg['SARIMA'] = fit1.predict(start=test.index[0].date(),
                                                                        end=self.get_today().date(), dynamic=True)
                                plt.figure(figsize=(16, 10))
                                plt.plot(train['value'], label='Train')
                                plt.plot(test['value'], label='Test')
                                plt.plot( y_hat_avg['SARIMA'], label='SARIMA')
                                plt.legend(loc='best')
                                plt.title(" SARIMA method \n  (RMSE = " + str(round(rms, 10)) + ", time = " + str(
                                    round(duration, 3)) + "c)", fontsize=35, fontweight='bold')
                                plt.savefig('media/arima.png')
                                pars.append(p7)
                          # ===========================================================================================
                            elif item == 'LSTM':
                                # transform data to be stationary
                                # transform data to be supervised learning
                                if analiz[0] != 'Стационарный':
                                    supervised = self.timeseries_to_supervised(self.difference(data_pred, 1), 1)
                                else:
                                    supervised = self.timeseries_to_supervised(data_pred, 1)
                                supervised_values = supervised.values
                                # split data into train and test-sets
                                train_lstm, test_lstm = supervised_values[0:-len(test)], supervised_values[-len(test):]
                                # transform the scale of the data
                                scaler, train_scaled, test_scaled = self.scale(train_lstm, test_lstm)
                                # walk-forward validation on the test data
                                error_scores, pred = list(), list()
                                for r in range(5):
                                    # fit the model
                                    lstm_model = self.fit_lstm(train_scaled, 1, 5, 5)
                                    # forecast the entire training dataset to build up state for forecasting
                                    train_reshaped = train_scaled[:, 0].reshape(len(train_scaled), 1, 1)
                                    lstm_model.predict(train_reshaped, batch_size=1)
                                    # walk-forward validation on the test data
                                    predictions = list()
                                    for i in range(len(test_scaled)):
                                        # make one-step forecast
                                        X, y = test_scaled[i, 0:-1], test_scaled[i, -1]
                                        yhat = self.forecast_lstm(lstm_model, 1, X)
                                        # invert scaling
                                        yhat = self.invert_scale(scaler, X, yhat)
                                        if analiz[0] != 'Стационарный':
                                            # invert differencing
                                            yhat = self.inverse_difference(data_pred, yhat, len(test_scaled) + 1 - i)
                                        # store forecast
                                        predictions.append(yhat)
                                    # report performance
                                    rms = sqrt(mean_squared_error(test.value, predictions))
                                    error_scores.append(rms)
                                    pred.append(predictions)
                                rms = np.array(error_scores).min()
                                i_min = error_scores.index(rms)
                                predictions = pred[i_min]
                                duration = time.time() - start
                                plt.figure(figsize=(16, 10))
                                plt.plot(train.index, train['value'], label='Train')
                                plt.plot(test.index, test['value'], label='Test')
                                plt.plot(test.index, predictions, label='LSTM')
                                plt.legend(loc='best')
                                plt.title("LSTM \n (RMSE = " + str(round(rms, 10)) + ", time = " + str(
                                    round(duration, 3)) + "c)", fontsize=35, fontweight='bold')
                                plt.savefig('media/lstm.png')
                                pars.append(None)
                                # # ===========================================================================================
                            rms_arr.append(rms)
                        obj.data_pred = data_pred
                        i = rms_arr.index(np.array(rms_arr).min())
                        if i < 7:
                            obj.pars = pars[i]
                        obj.method = methods[i]
                        obj.data_max = np.array(data_pred).max()
                        obj.data_min = np.array(data_pred).min()
                        obj.data_mean = np.array(data_pred).mean().round()
                        obj.data_std = np.array(data_pred).std().round()
                        obj.rms_min = round(np.array(rms_arr).min(), 10)
                        obj.analiz = analiz
                    except Containers.DoesNotExist:
                        pass
            except Modules.DoesNotExist:
                pass
        else:
            obj = None
        return obj

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_chosen'] = True
        context['title'] = 'Аналитика'
        context['methods'] = ['/media/' + x for x in os.listdir('media')]  # рисунки
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("confirm"):  # запрос пришел от кнопки
            str = request.POST['confirm']
            method_list = str.split('/')
            dict_params = ast.literal_eval(method_list[1])
            json_params = json.dumps(dict_params, indent=4)
            method = get_object_or_404(Methods, me_method=method_list[0])
            Modules.objects.filter(m_module=self.kwargs['slug']).update(m_method=method, m_params=json_params)
        return HttpResponseRedirect("/")