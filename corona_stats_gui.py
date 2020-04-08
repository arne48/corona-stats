from PyQt5 import (uic, QtWidgets, QtCore)
from PyQt5.QtWidgets import (QApplication, QCheckBox, QPushButton, QListWidget, QListWidgetItem, QWidget, QVBoxLayout)
from corona_stats import *
from utilities import get_names_of_countries
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import logging
import random

logging.basicConfig(filename='corona_stats.log', level=logging.INFO)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.ax2 = self.axes.twinx()
        self.main_color = 'blue'
        self.secondary_color = 'red'

        #self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        self.axes.plot([], [], 'r')

    def update_figure(self, cases, dates, sec_data=None, cases_log=False, sec_log=False, sec_label='',
                      sec_lin_reg=False):
        self.axes.cla()
        self.axes.set_ylabel('Confirmed', color=self.main_color)
        self.axes.tick_params(axis='y', labelcolor=self.main_color)
        self.axes.set_xlabel('Date')
        self.axes.grid(color='b', linestyle='-', linewidth=0.2)
        #plt.xticks(rotation=70)

        if cases_log:
            self.axes.set_yscale('log')
        self.axes.plot(dates, cases, label='cases', color=self.main_color)

        if sec_data is not None:
            self.ax2.cla()
            self.ax2.set_ylabel(sec_label, color=self.secondary_color)
            self.ax2.tick_params(axis='y', labelcolor=self.secondary_color)
            if sec_log:
                self.ax2.set_yscale('log')
            self.ax2.plot(dates, sec_data, label=sec_label, color=self.secondary_color)
            if sec_lin_reg:
                regression_data = get_linear_regression(np.array(sec_data), dates)
                self.ax2.plot(dates, regression_data, label='LinReg', color='green')
        self.draw()


# QT Begin Stuff
Form, Window = uic.loadUiType('corona-stats.ui')
app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)
visualization = MplCanvas(width=5, height=4, dpi=100)
sld_min_template = 'Min: '
sld_max_template = 'Max: '


def populate_country_lists():
    # Add Countries
    country_list = get_names_of_countries(CONFIRMED_DATA)
    for n in country_list:
        itm = QListWidgetItem(n)
        form.lst_country_main.addItem(itm)
        form.lst_country_main.setCurrentRow(0)
    for n in country_list:
        itm = QListWidgetItem(n)
        form.lst_country_sec.addItem(itm)
        form.lst_country_sec.setCurrentRow(0)


def setup_sliders():
    min_str = DATE_FIELDS[0]
    max_str = DATE_FIELDS[-1]
    slider_length = len(DATE_FIELDS)

    form.lbl_sld_min.setText(sld_min_template + min_str)
    form.sld_min.setMinimum(0)
    form.sld_min.setMaximum(slider_length - 1)
    form.sld_min.setSliderPosition(0)

    form.lbl_sld_max.setText(sld_max_template + max_str)
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

    # Get Primary Data
    country_name = form.lst_country_main.selectedItems()[0].text()
    primary_data = get_data_of_country(CONFIRMED_DATA, country_name)

    # Check for log settings
    primary_in_log = form.chk_cases_in_log.isChecked()
    secondary_in_log = form.chk_second_in_log.isChecked()

    # Check for Linear Regression
    secondary_linear_regression = form.chk_second_lin_reg.isChecked()

    # Check for Secondary Data
    secondary_data = None
    secondary_data_label = ''
    if form.grp_options.isChecked():
        if form.tgl_plot_d_inc.isChecked():
            secondary_data = get_daily_change(primary_data)
            secondary_data_label = 'Daily Increase'
        if form.tgl_plot_inf_rt.isChecked():
            secondary_data = get_infection_rate(primary_data)
            secondary_data_label = 'Infection Rate'
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

    limited_primary_data = primary_data[min_value:max_value]
    limited_dates = DATE_FIELDS[min_value:max_value]
    if secondary_data is not None:
        limited_secondary_data = secondary_data[min_value:max_value]
    else:
        limited_secondary_data = None

    visualization.update_figure(limited_primary_data, limited_dates, sec_data=limited_secondary_data,
                                cases_log=primary_in_log, sec_log=secondary_in_log, sec_label=secondary_data_label,
                                sec_lin_reg=secondary_linear_regression)


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
    form.lbl_sld_max.setText(sld_max_template + DATE_FIELDS[value])


def min_slider_handler():
    value = form.sld_min.value()
    form.lbl_sld_min.setText(sld_min_template + DATE_FIELDS[value])


def connect_signals():
    form.btn_plot.clicked.connect(plot_with_options)
    form.tgl_compare_countries.toggled.connect(compare_handler)
    form.grp_options.clicked.connect(option_handler)
    form.sld_max.sliderMoved.connect(max_slider_handler)
    form.sld_min.sliderMoved.connect(min_slider_handler)


populate_country_lists()
attach_mpl_viz()
setup_sliders()
connect_signals()
window.show()
app.exec_()
