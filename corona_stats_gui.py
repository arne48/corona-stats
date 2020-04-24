from PyQt5 import (uic, QtWidgets, QtCore)
from PyQt5.QtWidgets import (QApplication, QCheckBox, QPushButton, QListWidget, QListWidgetItem, QWidget, QVBoxLayout)
from corona_stats import *
from utilities import get_names_of_countries
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.ax2 = self.axes.twinx()
        self.primary_confirmed_color = 'blue'
        self.primary_dead_color = 'orange'
        self.primary_recovered_color = 'fuchsia'
        self.secondary_color = 'red'
        self.secondary_linreg_color = 'green'

        #self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        self.axes.plot([], [], 'r')

    def update_figure(self, prim_data, dates, prim_log=False, prim_dead=False, prim_dead_data=None, prim_recov=False,
                      prim_recov_data=None, sec_data=None, sec_log=False, sec_label='', sec_lin_reg=False,
                      sec_clear=False):
        self.axes.cla()
        self.axes.set_ylabel('Confirmed', color=self.primary_confirmed_color)
        self.axes.tick_params(axis='y', labelcolor=self.primary_confirmed_color)
        self.axes.set_xlabel('Date')
        self.axes.grid(color='b', linestyle='-', linewidth=0.2)

        # Rotate all labels individually
        for tick in self.axes.get_xticklabels():
            tick.set_rotation(70)

        if sec_data is not None:
            self.ax2.cla()
            self.ax2.set_ylabel(sec_label, color=self.secondary_color)
            self.ax2.tick_params(axis='y', labelcolor=self.secondary_color)
            if sec_log:
                self.ax2.set_yscale('log')
            self.ax2.plot(dates, sec_data, label=sec_label, color=self.secondary_color)
            if sec_lin_reg:
                regression_data = get_linear_regression(np.array(sec_data), dates)
                self.ax2.plot(dates, regression_data, label='LinReg', color=self.secondary_linreg_color)

            self.ax2.legend(loc=9)
        elif sec_clear:
            self.ax2.cla()

        # Plot primary data after secondary data so axis.cla() doesn't fuck up the graph
        if prim_log:
            self.axes.set_yscale('log')

        self.axes.plot(dates, prim_data, label='Confirmed', color=self.primary_confirmed_color)

        if prim_dead:
            self.axes.plot(dates, prim_dead_data, label='Dead', color=self.primary_dead_color)

        if prim_recov:
            self.axes.plot(dates, prim_recov_data, label='Recovered', color=self.primary_recovered_color)

        self.axes.legend(loc=2)
        self.draw()


# QT Begin Stuff
Form, Window = uic.loadUiType('corona-stats.ui')
app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)
visualization = MplCanvas(width=5, height=4, dpi=100)
sld_min_prefix = 'Min: '
sld_max_prefix = 'Max: '
global_death_rate = 0.0


def populate_country_lists():
    # Add Countries
    country_list = get_names_of_countries(CONFIRMED_DATA)
    death_rates = list()
    for n in country_list:
        total_cases = get_data_of_country(CONFIRMED_DATA, n)[-1]
        total_deaths = get_data_of_country(DEATH_DATA, n)[-1]
        death_rate = total_deaths/total_cases
        death_rates.append(death_rate)
        itm1 = QListWidgetItem('{} ({:f})'.format(n, death_rate))
        form.lst_country_main.addItem(itm1)
        itm2 = QListWidgetItem('{} ({:f})'.format(n, death_rate))
        form.lst_country_sec.addItem(itm2)
    form.lst_country_main.setCurrentRow(0)
    form.lst_country_sec.setCurrentRow(0)
    form.lbl_status_content.setText('Global death rate is {:f}'.format(sum(death_rates) / len(death_rates)))
    return sum(death_rates) / len(death_rates)


def setup_sliders():
    min_str = DATE_FIELDS[0]
    max_str = DATE_FIELDS[-1]
    slider_length = len(DATE_FIELDS)

    form.lbl_sld_min.setText(sld_min_prefix + min_str)
    form.sld_min.setMinimum(0)
    form.sld_min.setMaximum(slider_length - 1)
    form.sld_min.setSliderPosition(0)

    form.lbl_sld_max.setText(sld_max_prefix + max_str)
    form.sld_max.setMinimum(0)
    form.sld_max.setMaximum(slider_length - 1)
    form.sld_max.setSliderPosition(slider_length - 1)


def attach_mpl_viz():
    # Add Visualization
    form.vlay_viz.addWidget(visualization)


def plot_with_options():
    # Get Limits
    min_value = form.sld_min.value()
    max_value = form.sld_max.value()

    # Get Primary Data and split country name from the appended death rate
    country_name = str(form.lst_country_main.selectedItems()[0].text()).split(' ')[0]
    primary_data = get_data_of_country(CONFIRMED_DATA, country_name)

    # Check for additional Primary Data
    plot_primary_dead = form.chk_main_plt_dead.isChecked()
    limited_primary_dead = None
    plot_primary_recovered = form.chk_main_plt_recov.isChecked()
    limited_primary_recovered = None

    # Check for log settings
    primary_in_log = form.chk_cases_in_log.isChecked()
    secondary_in_log = form.chk_second_in_log.isChecked()

    # Check for Linear Regression
    secondary_linear_regression = form.chk_second_lin_reg.isChecked()

    # Check for Secondary Data
    secondary_data = None
    secondary_data_label = ''

    if form.grp_options.isChecked():
        form.lbl_status_content.setText('Global death rate is {:f}'.format(global_death_rate))
        secondary_clear = False
        if form.tgl_plot_d_inc.isChecked():
            secondary_data = get_daily_change(primary_data)
            secondary_data_label = 'Daily Increase'
        if form.tgl_plot_inf_rt.isChecked():
            secondary_data, status = get_infection_rate(primary_data)
            secondary_data_label = 'Infection Rate'
            form.lbl_status_content.setText(status)
        if form.tgl_plot_recov.isChecked():
            secondary_data = get_data_of_country(RECOVERED_DATA, country_name)
            secondary_data_label = 'Recovered'
        if form.tgl_plot_dead.isChecked():
            secondary_data = get_data_of_country(DEATH_DATA, country_name)
            secondary_data_label = 'Deaths'
        if form.tgl_compare_countries.isChecked():
            secondary_country_name = form.lst_country_sec.selectedItems()[0].text()
            secondary_data = get_data_of_country(CONFIRMED_DATA, secondary_country_name)
            secondary_data_label = secondary_country_name
    else:
        secondary_clear = True

    limited_primary_data = primary_data[min_value:max_value]
    limited_dates = DATE_FIELDS[min_value:max_value]

    if plot_primary_dead:
        primary_dead = get_data_of_country(DEATH_DATA, country_name)
        limited_primary_dead = primary_dead[min_value:max_value]
    if plot_primary_recovered:
        primary_recovered = get_data_of_country(RECOVERED_DATA, country_name)
        limited_primary_recovered = primary_recovered[min_value:max_value]

    if secondary_data is not None:
        limited_secondary_data = secondary_data[min_value:max_value]
    else:
        limited_secondary_data = None

    visualization.update_figure(limited_primary_data, limited_dates, prim_log=primary_in_log,
                                prim_dead=plot_primary_dead, prim_dead_data=limited_primary_dead,
                                prim_recov=plot_primary_recovered, prim_recov_data=limited_primary_recovered,
                                sec_data=limited_secondary_data, sec_log=secondary_in_log,
                                sec_label=secondary_data_label, sec_lin_reg=secondary_linear_regression,
                                sec_clear=secondary_clear)


def set_box_enabled(box, enabled):
    if enabled:
        box.setEnabled(True)
    else:
        box.setChecked(False)
        box.setEnabled(False)


def compare_handler():
    if form.tgl_compare_countries.isChecked():
        form.lst_country_sec.setEnabled(True)
    else:
        form.lst_country_sec.setEnabled(False)


def option_handler():
    if form.grp_options.isChecked():
        set_box_enabled(form.chk_second_in_log, True)
        set_box_enabled(form.chk_second_lin_reg, True)
    else:
        set_box_enabled(form.chk_second_in_log, False)
        set_box_enabled(form.chk_second_lin_reg, False)
        form.lst_country_sec.setEnabled(False)


def max_slider_handler():
    value = form.sld_max.value()
    form.lbl_sld_max.setText(sld_max_prefix + DATE_FIELDS[value])
    #plot_with_options()


def min_slider_handler():
    value = form.sld_min.value()
    form.lbl_sld_min.setText(sld_min_prefix + DATE_FIELDS[value])
    #plot_with_options()


def connect_signals():
    form.btn_plot.clicked.connect(plot_with_options)
    form.tgl_compare_countries.toggled.connect(compare_handler)
    form.grp_options.clicked.connect(option_handler)
    form.sld_max.valueChanged.connect(max_slider_handler)
    form.sld_min.valueChanged.connect(min_slider_handler)


global_death_rate = populate_country_lists()
attach_mpl_viz()
setup_sliders()
connect_signals()
window.show()
app.exec_()
