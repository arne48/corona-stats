import matplotlib.pyplot as plt
from utilities import get_data_of_country
from metrics import *


def show_single_country(name, data, date_fields, show_daily_increase=False, cases_in_log=False, increases_in_log=False):
    country_data = get_data_of_country(data, name)
    fig, ax1 = plt.subplots()

    color = 'blue'
    ax1.set_ylabel('People', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xlabel('Date')
    ax1.grid(color='b', linestyle='-', linewidth=0.2)
    plt.xticks(rotation=70)
    if cases_in_log:
        ax1.set_yscale('log')
    ax1.plot(date_fields, country_data, label='cases', color=color)

    if show_daily_increase:
        change_data = get_daily_change(country_data)
        ax2 = ax1.twinx()
        color = 'red'
        ax2.set_ylabel('Increase', color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        if increases_in_log:
            ax2.set_yscale('log')

        ax2.plot(date_fields, change_data, label='increase', color=color)

    fig.legend(loc="upper right")
    plt.show()


def compare_two_countries(first, second, confirmed_data, date_fields, cases_in_log=False):
    first_country = get_data_of_country(confirmed_data, first)
    second_country = get_data_of_country(confirmed_data, second)

    plt.plot(date_fields, first_country, label=first)
    plt.plot(date_fields, second_country, label=second)
    plt.xlabel('Date')
    plt.xticks(rotation=70)
    plt.ylabel('People')
    if cases_in_log:
        plt.yscale('log')
    plt.grid(color='b', linestyle='-', linewidth=0.2)
    plt.legend()
    plt.show()

