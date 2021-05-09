from .models import *
import pandas as pd
import numpy as np
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Max
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import statsmodels.api as sm
from pandas import Series, DataFrame, concat
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
from scipy.stats import anderson
from statsmodels.tsa.seasonal import seasonal_decompose


class MyMixin(object):
    def get_today(self):
        try:
            date_last = Containers.objects.latest('c_date')
            dt = datetime.datetime.combine(date_last.c_date.date(), datetime.time(6, 0, 0))
        except Containers.DoesNotExist:
            dt = None
        return dt

    def get_count_days(self, f, predictions):
        count = 0
        for incr in predictions:
            if f > 100:
                break
            f += incr
            count += 1
        return count

    def get_pred(self, module):
        labels_pred, data_pred, predictions = [], [], []
        # формирование временного ряда
        queryset = Containers.objects.filter(c_module__m_module=module.m_module, c_incr__isnull=False)
        object = Containers.objects.filter(c_module__m_module=module.m_module, c_curr=module.m_height).latest('c_date')
        days = (self.get_today().date() - object.c_date.date()).days
        for it in queryset:
            labels_pred.append(it.c_date.date())
            data_pred.append(it.c_incr)
        dd = np.asarray(data_pred)
        df = pd.DataFrame(data=dd, index=pd.to_datetime(labels_pred), columns=['value'])
        # df = df.resample('D').mean()  # уменьшение количества выбросов
        obj = get_object_or_404(Containers, c_module__m_module=module.m_module, c_date=self.get_today(), c_is_collected=False)
        fill_level = obj.fill_level
        if fill_level >= 100:
            module.m_plan = self.get_today().date()
        else:
            max_period = Analitics.objects.filter(a_module__m_module=module.m_module).aggregate(Max('a_period'))
            forecast_period = int(max_period['a_period__max']) + 2 - days
            method = str(module.m_method)
            if (method == 'Наивный подход'):
                predictions = [dd[len(dd) - 1]] * forecast_period
            elif (method == 'Простое среднее'):
                predictions = [df['value'].mean()] * forecast_period
            elif (method == 'Скользящее среднее'):
                predictions = [df['value'].rolling(48).mean().iloc[-1]] * forecast_period
            elif (method == 'Простое экспоненциальное сглаживание'):
                fit = SimpleExpSmoothing(np.asarray(df['value'])).fit(smoothing_level=module.params['s_l'],
                                                                      optimized=False)
                predictions = fit.forecast(forecast_period)
            elif (method == 'Метод линейного тренда Холта'):
                fit = Holt(np.asarray(df['value'])).fit(smoothing_level=module.params['s_l'],
                                                        smoothing_slope=module.params['s_s'])
                predictions = fit.forecast(forecast_period)
            elif (method == 'Метод Холта-Винтерса'):
                fit = ExponentialSmoothing(np.asarray(df['value']), seasonal_periods=module.params['s_p'],
                                           trend=module.params['t'], seasonal=module.params['s'], ).fit()
                predictions = fit.forecast(forecast_period)
            elif (method == 'SARIMA'):
                fit = sm.tsa.statespace.SARIMAX(df.value, order=(module.params['p'], module.params['d'], module.params['q']),
                                                seasonal_order=(module.params['P'], module.params['D'],
                                                                module.params['Q'], module.params['m'])).fit()
                s_date = self.get_today() + datetime.timedelta(1)
                e_date = self.get_today() + datetime.timedelta(forecast_period)
                predictions = fit.predict(start=s_date.date(), end=e_date.date(), dynamic=True)
            elif (method == 'LSTM'):
                analiz, d_7 = self.stationarity(df.value)
                for i in range(forecast_period):
                    if analiz[0] != 'Стационарный':
                        data_pred = self.difference(data_pred, 1)
                    supervised = self.timeseries_to_supervised(data_pred, 1)
                    supervised_values = supervised.values
                    train_lstm = supervised_values[0:len(supervised_values)-1]
                    test_lstm = supervised_values[len(supervised_values)-1:]
                    scaler = MinMaxScaler(feature_range=(-1, 1))
                    scaler = scaler.fit(train_lstm)
                    # transform train
                    train = train_lstm.reshape(train_lstm.shape[0], train_lstm.shape[1])
                    train_scaled = scaler.transform(train)
                    # fit the model
                    lstm_model = self.fit_lstm(train_scaled, 1, 5, 5)
                    # forecast the entire training dataset to build up state for forecasting
                    train_reshaped = train_scaled[:, 0].reshape(len(train_scaled), 1, 1)
                    lstm_model.predict(train_reshaped, batch_size=1)
                    # walk-forward validation on the test data
                    # transform test
                    test = test_lstm.reshape(test_lstm.shape[0], test_lstm.shape[1])
                    test_scaled = scaler.transform(test)
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
                        predictions.append(round(yhat))
                        data_pred.append(yhat)
            count = self.get_count_days(fill_level, predictions)
            date_plan = self.get_today() + datetime.timedelta(days=count)
            module.m_plan = date_plan.date()
        module.save()
        return

        # Анализ ряда
        # https: // habr.com / ru / post / 207160 / проверка ряда на стационарность
    def stationarity(self, data):
        analiz = []
        train_data = np.array(data)
        tst = sm.tsa.adfuller(data)
        train_diff = data.diff(periods=1).dropna()
        if tst[0] > tst[4]['5%']:
            tst = sm.tsa.adfuller(train_diff)
            if tst[0] > tst[4]['5%']:
                d = [2]
                analiz.append('Нестационарный')
            else:
                analiz.append('Интегрированный 1-го порядка')
                d = [1]
        else:
            analiz.append('Стационарный')
            d = [0]

        # homogenety test
        std = np.array(data).std()
        mean = np.array(data).mean()
        if (std / mean).round() * 100 <= 33:
            analiz.append(', однородный')
        else:
            analiz.append(', неоднородный')
        for i in range(0, len(data)):
            if (train_data[i] <= mean - 3 * std) or (train_data[i] >= mean + 3 * std):
                analiz.append(', имеются аномальные выбросы')
        # normality test
        # https://www.machinelearningmastery.ru/a-gentle-introduction-to-normality-tests-in-python/

        if analiz[0] != 'Стационарный':
            result = anderson(train_diff)
        else:
            result = anderson(train_data)
        p = False
        for i in range(len(result.critical_values)):
            if result.statistic < result.critical_values[i]:
                p = True
                break
        if p:
            analiz.append(', нормальное распределение')
        else:
            analiz.append(', распределение не является нормальным')
        return analiz, d

    # create a differenced series
    def difference(self, dataset, interval=1):
        diff = []
        for i in range(interval, len(dataset)):
            value = dataset[i] - dataset[i - interval]
            diff.append(value)
        return Series(diff)

    # invert differenced value
    def inverse_difference(self, history, yhat, interval=1):
        return yhat + history[-interval]

    # frame a sequence as a supervised learning problem
    def timeseries_to_supervised(self, data, lag=1):
        df = DataFrame(data)
        columns = [df.shift(i) for i in range(1, lag + 1)]
        columns.append(df)
        df = concat(columns, axis=1)
        df.fillna(0, inplace=True)
        return df

    # scale train and test data to [-1, 1]
    def scale(self, train, test):
        # fit scaler
        scaler = MinMaxScaler(feature_range=(-1, 1))
        scaler = scaler.fit(train)
        # transform train
        train = train.reshape(train.shape[0], train.shape[1])
        train_scaled = scaler.transform(train)
        # transform test
        test = test.reshape(test.shape[0], test.shape[1])
        test_scaled = scaler.transform(test)
        return scaler, train_scaled, test_scaled

    # fit an LSTM network to training data
    def fit_lstm(self, train, batch_size, nb_epoch, neurons):
        X, y = train[:, 0:-1], train[:, -1]
        X = X.reshape(X.shape[0], 1, X.shape[1])
        model = Sequential()
        model.add(LSTM(neurons, batch_input_shape=(batch_size, X.shape[1], X.shape[2]), stateful=True))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')
        for i in range(nb_epoch):
            model.fit(X, y, epochs=1, batch_size=batch_size, verbose=0, shuffle=False)
            model.reset_states()
        return model

    # make a one-step forecast
    def forecast_lstm(self, model, batch_size, X):
        X = X.reshape(1, 1, len(X))
        yhat = model.predict(X, batch_size=batch_size)
        return yhat[0, 0]

    # inverse scaling for a forecasted value
    def invert_scale(self, scaler, X, value):
        new_row = [x for x in X] + [value]
        array = np.array(new_row)
        array = array.reshape(1, len(array))
        inverted = scaler.inverse_transform(array)
        return inverted[0, -1]

