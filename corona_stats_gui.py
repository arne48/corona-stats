from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QCheckBox, QPushButton, QListWidget, QListWidgetItem, QWidget)
from corona_stats import *
from utilities import get_names_of_countries
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

Form, Window = uic.loadUiType('corona-stats.ui')
app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

# Add Countries
country_list = get_names_of_countries(CONFIRMED_DATA)
for n in country_list:
    itm = QListWidgetItem(n)
    form.lst_country11.addItem(itm)
for n in country_list:
    itm = QListWidgetItem(n)
    form.lst_country21.addItem(itm)
for n in country_list:
    itm = QListWidgetItem(n)
    form.lst_country22.addItem(itm)


# Button Callbacks
def tab1_btn_clicked():
    country = form.lst_country11.selectedItems()[0].text()
    confirmed_cases_log1 = form.chk_confirmed_cases_log1.checkState()
    daily_increase_log1 = form.chk_daily_inc_log1.checkState()
    window.setCurrentWidget(window.findChild(QWidget, 'tab_viz'))


def tab2_btn_clicked():
    first_country = form.lst_country21.selectedItems()[0].text()
    second_country = form.lst_country22.selectedItems()[0].text()
    confirmed_cases_log2 = form.chk_confirmed_cases_log2.checkState()
    window.setCurrentWidget(window.findChild(QWidget, 'tab_viz'))


# Connect Buttons
form.btn_plot1.clicked.connect(tab1_btn_clicked)
form.btn_plot2.clicked.connect(tab2_btn_clicked)

window.show()
app.exec_()
