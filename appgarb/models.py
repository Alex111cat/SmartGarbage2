from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import datetime, json
from django.urls import reverse
from django.utils.timezone import now


class Streets(models.Model):
    s_street = models.CharField(max_length=50, db_index=True, unique=True,  verbose_name='Название улицы')

    def __str__(self):
        return self.s_street

    class Meta:
        verbose_name = 'Улица'
        verbose_name_plural = 'Улицы'
        ordering = ['s_street']

class Modules(models.Model):
    m_module = models.CharField(max_length=4, blank=False, db_index=True, verbose_name='Модуль')
    m_street = models.ForeignKey('Streets', on_delete=models.PROTECT, verbose_name='Название улицы')
    m_house = models.CharField(max_length=10, blank=False, verbose_name='Номер дома')
    m_building = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Корпус')
    m_entrance = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=1, blank=False, verbose_name='Подъезд')
    m_height = models.PositiveSmallIntegerField(blank=False, verbose_name='Высота установки, в см')
    m_start = models.DateField(default=datetime.date.today(), verbose_name='Дата установки')
    m_is_active = models.BooleanField(default=True, verbose_name='Состояние')
    m_slug = models.SlugField(max_length=255, verbose_name='Url', unique=True)
    m_cont = models.PositiveSmallIntegerField(default=100, blank=False, verbose_name='Высота контейнера, в см')
    m_pipe = models.PositiveSmallIntegerField(default=150, blank=False, verbose_name='Высота мусоропровода')
    m_method = models.ForeignKey('Methods', on_delete=models.PROTECT, default=1, blank=True, verbose_name='Название метода')
    m_params = models.TextField(default='{}', verbose_name='Параметры метода')
    m_plan = models.DateField(default=datetime.date.today(), verbose_name='Плановая дата вывоза')


    def __str__(self):
        return self.m_module

    def get_absolute_url(self):
        return reverse('module', kwargs={'slug': self.m_slug})

    def get_absolute_url_fire(self):
        return reverse('fire', kwargs={'slug': self.m_slug})

    def get_address(self):
        if self.m_building:
            return  'д.' + self.m_house + ', к.' + str(self.m_building) + ', под.' + str(self.m_entrance)
        else:
            return  'д.' + self.m_house + ', под.' + str(self.m_entrance)
    get_address.short_description = "Адрес"
    address = property(get_address)

    def get_params(self):
        return json.loads(self.m_params)
    params = property(get_params)

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        unique_together = ['m_street', 'm_house', 'm_building', 'm_entrance']
        ordering = ['m_module']

class Containers(models.Model):
    c_module = models.ForeignKey('Modules', on_delete=models.CASCADE, verbose_name='Модуль')
    c_date = models.DateTimeField(default=datetime.datetime.combine(now().date(), datetime.time(6, 0, 0)),
                                  blank=False, verbose_name = 'Дата измерения')
    c_curr = models.PositiveSmallIntegerField(default=None, null=True, blank=True, verbose_name='Дистанция до мусора, см')
    c_is_collected = models.BooleanField(default=False, blank=False, verbose_name='Мусор вывезен')
    c_incr = models.PositiveSmallIntegerField(default=None, null=True, blank=True, verbose_name='Суточный прирост, %')

    def __unicode__(self):
        return self.c_module, str(self.c_date), str(self.c_curr)

    # def get_absolute_url(self):
    #     return reverse('module', kwargs={'slug': self.c_module})

    def get_fill(self):
        if self.c_curr:
            return int(round((self.c_module.m_height - self.c_curr) * 100 / self.c_module.m_cont, 2))
    get_fill.short_description = "Уровень наполнения, %"
    fill_level = property(get_fill)

    # def get_absolute_url(self):
    #     return reverse('module', kwargs={'pk': self.pk})

    def get_procentage(self):
        if self.c_curr:
            if self.fill_level <= 50:
                bar_class = 'progress-bar-success'
            elif self.fill_level >= 90:
                bar_class = 'progress-bar-danger'
            elif 50 < self.fill_level < 90:
                bar_class = 'progress-bar-warning'
            return bar_class
    procentage = property(get_procentage)

    def get_chart_color(self):
        if self.c_curr:
            if self.fill_level <= 50:
                chart_color = '#4caf50'
            elif self.fill_level >= 90:
                chart_color = '#f44336'
            elif 50 < self.fill_level < 90:
                chart_color = '#ff9800'
            return chart_color
    chart_color = property(get_chart_color)

    class Meta:
        verbose_name = 'Контейнер'
        verbose_name_plural = 'Контейнеры'
        unique_together = ['c_module', 'c_date', 'c_is_collected']
        ordering = ['c_module', 'c_date', '-c_is_collected']

class Fire(models.Model):
    f_module = models.ForeignKey('Modules', on_delete=models.CASCADE, verbose_name='Модуль')
    f_alarm = models.DateTimeField(blank=False,  verbose_name='Дата и время')
    f_temp = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Температура')
    f_smoke = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Задымленность')

    def __unicode__(self):
        return self.f_module, self.f_alarm

    class Meta:
        verbose_name = 'Пожарная тревога'
        verbose_name_plural = 'Пожарная тревога'
        unique_together = ['f_module', 'f_alarm']
        ordering = ['f_module', 'f_alarm']

class Analitics(models.Model):
    a_module = models.ForeignKey('Modules',  on_delete=models.CASCADE, verbose_name='Модуль')
    a_date = models.DateTimeField(default=datetime.datetime.combine(now().date(), datetime.time(0, 0, 0)),
                                                                    blank=False, verbose_name='Дата вывоза')
    a_period = models.PositiveSmallIntegerField(blank=False, verbose_name='Период наполнения, в днях')
    a_fullness = models.PositiveSmallIntegerField(default=100, blank=True, null=True, verbose_name='Уровень наполнения, в %')

    def __unicode__(self):
        return self.a_module, self.a_date

    def get_date(self):
            return self.a_date.date()
    get_date.short_description = "Дата вывоза"
    date_collection = property(get_date)

    def get_average(self):
        return round(self.a_fullness/self.a_period ,1)
    get_average.short_description = "Среднесуточный прирост, %"
    incr_average = property(get_average)

    class Meta:
        verbose_name = 'Аналитика'
        verbose_name_plural = 'Аналитика'
        unique_together = ['a_module', 'a_date']
        ordering = ['a_module', 'a_date']

class Methods(models.Model):
    me_method = models.CharField(max_length=40, db_index=True, unique=True,  verbose_name='Название метода')

    def __str__(self):
        return self.me_method

    class Meta:
        verbose_name = 'Метод'
        verbose_name_plural = 'Методы'
        ordering = ['id']
