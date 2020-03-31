import logging
import pandas as pd
from github_raw import get_file_from_link
from visualizer import show_single_country, compare_two_countries
from utilities import *
from metrics import *

DEFAULT_CONFIRMED_PATH = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
DEFAULT_DEATHS_PATH = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
DEFAULT_RECOVERED_PATH = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

CONFIRMED_FILE = get_file_from_link(DEFAULT_CONFIRMED_PATH)
DEATH_FILE = get_file_from_link(DEFAULT_DEATHS_PATH)
RECOVERED_FILE = get_file_from_link(DEFAULT_RECOVERED_PATH)

CONFIRMED_DATA, DATE_FIELDS = sanitize_data(pd.read_csv(CONFIRMED_FILE))
DEATH_DATA, DATE_FIELDS = sanitize_data(pd.read_csv(DEATH_FILE))
REOVERED_DATA, DATE_FIELDS = sanitize_data(pd.read_csv(RECOVERED_FILE))


def main():
    # Show single Country
    show_single_country('Germany', CONFIRMED_DATA, DATE_FIELDS, show_daily_increase=True, cases_in_log=False,
                        increases_in_log=False)

    # Compare two countries
    #compare_two_countries('Germany', 'Japan', confirmed_data, date_fields, cases_in_log=True)


if __name__ == '__main__':
    logging.basicConfig(filename='corona_stats.log', level=logging.INFO)
    main()
