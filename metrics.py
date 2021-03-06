import logging
import numpy as np


def get_slope(data, position):
    np_data = np.array(data).astype(np.float64)
    data_length = len(data)

    if position <= 0:
        return np.gradient([np_data[position], np_data[position+1]])[0]
    elif position > data_length-1:
        return np.gradient([np_data[position - 1], np_data[position]])[0]
    else:
        return np.gradient([np_data[position-1], np_data[position+1]])[0]


def get_linear_regression(data, dates):
    x_axis = np.arange(len(dates))
    m, b = np.polyfit(x_axis.astype(np.float64), data.astype(np.float64), 1)
    ret_val = list(m * x + b for x in x_axis)

    # Set negative values to zero
    ret_val = np.array(ret_val)
    ret_val[ret_val < 0] = 0
    return ret_val


def get_daily_change(data):
    data_out = [0]
    for n, d in enumerate(data[1:]):
        if n > 0:
            data_out.append(data[n] - data[n-1])
    data_out.append(data_out[-1])
    return data_out


def get_infection_rate(data):
    data_out = [1.0]
    for n, d in enumerate(data[1:]):
        if n > 0:
            try:
                data_out.append(float(data[n]) / float(data[n-1]))
            except ZeroDivisionError:
                data_out.append(float(data[n-1]))
    data_out.append(data_out[-1])
    #print('Last infection rate: ' + str(data_out[-1]))
    #print('Highest infection rate: ' + str(max(data_out)))
    status = 'Highest infection rate: {} | Latest infection rate: {}'.format(str(max(data_out)), str(data_out[-1]))
    # find and replace 0.0 values and replace them with 1.0
    for n, i in enumerate(data_out):
        if i == 0.0:
            data_out[n] = 1.0
    return data_out, status


def get_death_rate(death_data, confirmed_data):
    ret_val = list()
    for n, d in enumerate(death_data):
        if d < 1.0:
            ret_val.append(0.0)
        else:
            ret_val.append(d / confirmed_data[n])
    return ret_val
