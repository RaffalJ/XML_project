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

CARMOT_URL = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/datastructure/ESTAT/DSD_road_eqr_carmot"
url = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/nama_10_gdp/.CP_MEUR.B1GQ.DE+FR+IT?startPeriod=2010&endPeriod=2013"

class Data:
    def __init__(self, name):
        self.name = name
        self.years = []
        self.values = []

    def addEntry(self, year, value):
        self.years.append(year)
        self.values.append(value)

class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi("1.ui", self)

        self.setWindowTitle("")

        # Items need to be added in loop with addItem("") method from xml data when its added
        self.comboBox_country_PKB.addItems(["Kupa", "Dupa"])
        self.comboBox_country_PKB.currentIndexChanged.connect(self.selectionchange_PKB)

        self.comboBox_country_engines.addItems(["Kupa", "Dupa"])
        self.comboBox_country_engines.currentIndexChanged.connect(self.selectionchange_eng_country)

        self.comboBox_engine_type.addItems(["Kupa", "Dupa"])
        self.comboBox_engine_type.currentIndexChanged.connect(self.selectionchange_eng_type)

        self.spinBox_year1.valueChanged.connect(self.valuechange_year1)
        self.spinBox_year2.valueChanged.connect(self.valuechange_year2)

        self.addToolBar(NavigationToolbar(self.MplWidget_PKB.canvas, self))
        self.addToolBar(NavigationToolbar(self.MplWidget_engine.canvas, self))

    def parseDictionary(doc):
        countries = []
        iterator = 0
        values = doc.get("message:GenericData").get("message:DataSet").get("generic:Series")
        for value in values:
            valuesArr = value.get("generic:SeriesKey").get("generic:Value")
            for val in valuesArr:
                if val.get("@id") == "GEO":
                    countries.append(Data(val.get("@value")))
            objs = value.get("generic:Obs")
            for obj in objs:
                countries[iterator].addEntry(obj.get("generic:ObsDimension").get("@value"), obj.get("generic:ObsValue").get("@value"))
            iterator += 1
        return countries

    def assign_data():
        # narazie example z poprzedniego
        r = requests.get(url)

        doc = xmltodict.parse(r.content)
        countries = parseDictionary(doc)

        country_values = []
        for country in countries:
            country_values.append(country.values)

        data_list = []
        for i in range(0, 3):
            tmp_list = []
            for x in country_values[i]:
                tmp_list.append(float(x)/100)

            data = []
            data.append([10, 11, 12 ,13])
            data.append(tmp_list)
            data.append("Title")
            data.append("x")
            data.append("y")
            data_list.append(data)

    def selectionchange_PKB(self, index):
        countryPKB = index
        self.update_graph_PKB()

    def selectionchange_eng_country(self, index):
        country_engine = index
        self.update_graph_engine()

    def selectionchange_eng_type(self, index):
        type_of_engine = index
        self.update_graph_engine()

    def valuechange_year1(self):

        if spinBox_year1.value() < 1990:
            year1 = 1990
        else:
            if spinBox_year1.value() < year2:
                year1 = spinBox_year1.value()

        self.update_graph_PKB()
        self.update_graph_engine()

    def valuechange_year2(self):

        if spinBox_year2.value() < 1990:
            year2 = 1990
        else:
            if spinBox_year2.value() > year1:
                year2 = spinBox_year2.value()

        self.update_graph_PKB()
        self.update_graph_engine()

    def update_graph_PKB(self, country=country_PKB, year_start=year1, year_stop=year2):
        country_PKB_data = np.linspace(year_start, year_stop, (year_stop - year_start) + 1)
        t = np.linspace(year_start, year_stop, (year_stop - year_start) + 1)

        self.MplWidget_PKB.canvas.axes.clear()
        self.MplWidget_PKB.canvas.axes.plot(t, country_PKB_data)
        self.MplWidget_PKB.canvas.axes.legend(('year', 'PKB'), loc='upper right')
        self.MplWidget_PKB.canvas.axes.set_title('Country PKB')
        self.MplWidget_PKB.canvas.draw()

    def update_graph_engine(self, country=country_PKB, engine_type = type_of_engine, year_start=year1, year_stop=year2):
        # here im not sure of engine data structure

        # data = engine_data[country][engine_type]
        t = np.linspace(year_start, year_stop, (year_stop - year_start) + 1)
        data = np.linspace(year_start, year_stop, (year_stop - year_start) + 1)
        self.MplWidget_engine.canvas.axes.clear()
        self.MplWidget_engine.canvas.axes.plot(t, data)
        self.MplWidget_engine.canvas.axes.legend(('year', 'amount of cars'), loc='upper right')
        self.MplWidget_engine.canvas.axes.set_title('Cars bought by engine type')
        self.MplWidget_engine.canvas.draw()



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
