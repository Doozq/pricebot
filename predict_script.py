import numpy as np
import pandas as pd
import joblib
import catboost
import scipy
import sklearn
import yfinance as yf

from scipy.stats import boxcox
from scipy.special import inv_boxcox
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor

iterations_cat = 500
learning_rate_cat = 0.03
depth_cat = 8
l2_leaf_reg_cat = 7
box_cox_ch = 0


def box_cox(data, columnOld, columnNew):
    trans, lambda_ = boxcox(data[columnOld].values)
    data[columnNew] = trans
    return lambda_


def inv_box_cox(data, lambda_):
    return inv_boxcox(data, lambda_)


def diff(data, columnOld, columnNew):
    data[columnNew] = data[columnOld].diff()


def inv_diff(base, predict):
    summ = [i+j for i, j in zip(base[len(base)-len(predict)-1:-1], predict)]
    return np.array(summ).reshape(-1, 1)


def minmax(data, columnOld, columnNew):
    scaler = MinMaxScaler()
    data[columnNew] = scaler.fit_transform(data[columnOld].values.reshape(-1, 1))
    return scaler.fit(data[columnOld].values.reshape(-1, 1))


def inv_minmax(data, obj):
    return obj.inverse_transform(data).reshape(-1, 1)


def lag_fich(data, columnOld):
    prediction_window = 10
    prediction_columns = [columnOld]
    for i in range(1, prediction_window+1):
        col_name = f'shift_{i}'
        prediction_columns.append(col_name)
        data[col_name] = data[prediction_columns[0]].shift(i)

    return data[prediction_columns].dropna(), prediction_columns


def all_transform(dataf, pupu, box_cox_ch=1):
    if box_cox_ch == 1:
        lambda_dataf = box_cox(dataf, pupu, 'boxcox')
        data1 = dataf['boxcox'].copy()
        diff(dataf, 'boxcox', 'diff')
        return lambda_dataf, data1
    else:
        lambda_dataf = 0
        data1 = dataf[pupu].copy()
        diff(dataf, pupu, 'diff')
        return lambda_dataf, data1


def inv_all_transform(data1, data_test, lambda_data, box_cox_ch=1):
    if box_cox_ch == 1:
        inv_data_test_from_diff_to_boxcox = inv_diff(data1, data_test.values.reshape(-1, 1))
        inv_data_test = inv_boxcox(inv_data_test_from_diff_to_boxcox, lambda_data)
        return inv_data_test
    else:
        inv_data_test = inv_diff(data1, data_test.values.reshape(-1,1))
        return inv_data_test


def add_feature(name, feature, prediction_columns, high, low):
    prediction_columns.append(name)

    high[name] = feature[len(feature)-len(high):]
    low[name] = feature[len(feature)-len(low):]


def metrics(predicted, real):
    from sklearn.metrics import mean_squared_error
    print('mean_squared_error (MSE)', mean_squared_error(predicted, real))

    from sklearn.metrics import mean_absolute_error
    print('mean_absolute_error (MAE)', mean_absolute_error(predicted, real))

    from sklearn.metrics import mean_absolute_percentage_error
    print('mean_absolute_percentage_error (MAPE)', mean_absolute_percentage_error(predicted, real))
    
    from sklearn.metrics import r2_score
    print('r2_score (R^2)', r2_score(predicted, real))


def give_result(btcUsdDf):    
    high, low = preprocessing(btcUsdDf)
    return [low, high]


def preprocessing(btcUsdDf):
    low = btcUsdDf[:].copy()
    high = btcUsdDf[:].copy()
    close = btcUsdDf[:].copy()

    high_real = high['High'].copy()
    low_real = low['Low'].copy()
    lambda_high, high1 = all_transform(high, 'High', box_cox_ch)
    lambda_low, low1= all_transform(low, 'Low', box_cox_ch)
    high, prediction_columns = lag_fich(high, 'diff')
    low, prediction_columns = lag_fich(low, 'diff')
    return [give_high(high, prediction_columns, high1, lambda_high), give_low(low, prediction_columns, low1, lambda_low)]


def give_high(high, prediction_columns, high1, lambda_high):
    
    X = high[prediction_columns[1:]]
    y = high[prediction_columns[0]]


    high_x_train, high_x_test, high_train, high_test = train_test_split(X, y, test_size=0.33, random_state = 42, shuffle = False)

    high_x_train.fillna(value=0, inplace=True)
    high_x_test.fillna(value=0, inplace=True)
    high_train.fillna(value=0, inplace=True)
    high_test.fillna(value=0, inplace=True)

    regressor_high = CatBoostRegressor(
        iterations=iterations_cat,
        learning_rate=learning_rate_cat,
        depth=depth_cat,
        l2_leaf_reg=l2_leaf_reg_cat
    )
    regressor_high.fit(high_x_train, high_train)

    inv_high_test = inv_all_transform(high1, high_test, lambda_high, box_cox_ch)
    inv_high_x = inv_all_transform(high1, pd.Series(regressor_high.predict(high_x_test)), lambda_high, box_cox_ch)
    return inv_high_x[-1]


def give_low(low, prediction_columns, low1, lambda_low):

    X_low = low[prediction_columns[1:]]
    y_low = low[prediction_columns[0]]

    low_x_train, low_x_test, low_train, low_test = train_test_split(X_low, y_low, test_size=0.33, random_state = 42, shuffle = False)

    low_x_train.fillna(value=0, inplace=True)
    low_x_test.fillna(value=0, inplace=True)
    low_train.fillna(value=0, inplace=True)
    low_test.fillna(value=0, inplace=True)
    from catboost import CatBoostRegressor
    regressor_low = CatBoostRegressor(
        iterations=iterations_cat,
        learning_rate=learning_rate_cat,
        depth=depth_cat,
        l2_leaf_reg=l2_leaf_reg_cat
    )
    regressor_low.fit(low_x_train, low_train)

    inv_low_test = inv_all_transform(low1, low_test, lambda_low, box_cox_ch)
    inv_low_x = inv_all_transform(low1, pd.Series(regressor_low.predict(low_x_test)), lambda_low, box_cox_ch)

    return inv_low_x[-1]


def predict_crypto(data):
    low, high = give_result(data)

    message = {
        "Low": round(low[0], 3),
        "High": round(high[0], 3)
    }
    return message
