from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import matplotlib
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import numpy as np
import random

country_PKB = 0
country_engine = 0
type_of_engine = 0
year1 = 1990
year2 = 2014
PKB_data = [1, 2, 3, 4, 5]
engine_data = [1, 2, 3, 4, 5]
class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi("1.ui", self)

        self.setWindowTitle("PyQt5 & Matplotlib Example GUI")

        self.comboBox_country_PKB.currentIndexChanged.connect(self.selectionchange_PKB)
        self.comboBox_country_PKB.addItems(["Kupa", "Dupa"])
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

    def selectionchange_PKB(self, i):
        countryPKB = i
        update_graph_PKB()

    def update_graph_PKB(self, country=country_PKB, year_start = year1, year_stop = year2):

        country_PKB_data = PKB_data[country]
        t = np.linspace(year_start, year_stop, 1)

        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(t, country_PKB_data)
        self.MplWidget.canvas.axes.legend(('year', 'PKB'), loc='upper right')
        self.MplWidget.canvas.axes.set_title('Country PKB')
        self.MplWidget.canvas.draw()


    # def update_graph(self):
    #     fs = 500
    #     f = random.randint(1, 100)
    #     ts = 1 / fs
    #     length_of_signal = 100
    #     t = np.linspace(0, 1, length_of_signal)
    #
    #     cosinus_signal = np.cos(2 * np.pi * f * t)
    #     sinus_signal = np.sin(2 * np.pi * f * t)
    #
    #     self.MplWidget.canvas.axes.clear()
    #     self.MplWidget.canvas.axes.plot(t, cosinus_signal)
    #     self.MplWidget.canvas.axes.plot(t, sinus_signal)
    #     self.MplWidget.canvas.axes.legend(('cosinus', 'sinus'), loc='upper right')
    #     self.MplWidget.canvas.axes.set_title('Cosinus - Sinus Signal')
    #     self.MplWidget.canvas.draw()


app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()