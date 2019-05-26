from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import time
import os
import matplotlib

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import numpy as np
import sys
import requests
import xmltodict
import random

country_PKB = 0
country_engine = 0
type_of_engine = 0
engine_data = [1, 2, 3, 4]

# GLOBAL VARIABLES - FOR NOW
year1 = 2000
year2 = 2013
PKB_data = []
countries = []

CARMOT_URL = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/datastructure/ESTAT/DSD_road_eqr_carmot"
url = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/nama_10_gdp/.CP_MEUR.B1GQ."+"DE+FR+IT?startPeriod=2000&endPeriod=2013"

class Data:
    def __init__(self, name):
        self.name = name
        self.years = []
        self.values = []

    def addEntry(self, year, value):
        self.years.append(year)
        self.values.append(value)

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

def get_pkb_values():
    global year1, year2
    start_year = year1
    end_year = year2
    countries = "DE+FR+IT"
    url = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/nama_10_gdp/.CP_MEUR.B1GQ."+countries+"?startPeriod="+str(start_year)+"&endPeriod="+str(end_year)
    r = requests.get(url)
    doc = xmltodict.parse(r.content)
    countries = parseDictionary(doc)
    return countries

def update_pkb_values():
    global PKB_data, countries
    PKB_data.clear()
    data = get_pkb_values()
    for country in data:
        countries.append(country.name)
        tmp_values = []
        for value in country.values:
            tmp_values.append(int(float(value))/1000)
        PKB_data.append(tmp_values)

class MatplotlibWidget(QMainWindow):
    def __init__(self, data):
        global PKB_data, countries, year1, year2
        QMainWindow.__init__(self)

        loadUi("1.ui", self)
        self.setWindowTitle("")
        self.carMotData = data

        update_pkb_values()

        self.comboBox_country_PKB.addItems(countries)
        self.comboBox_country_PKB.currentIndexChanged.connect(self.selectionchange_PKB)

        self.comboBox_country_engines.addItems(countries)
        self.comboBox_country_engines.currentIndexChanged.connect(self.selectionchange_eng_country)

        self.comboBox_engine_type.addItems(["Diesel", "Benzine"])
        self.comboBox_engine_type.currentIndexChanged.connect(self.selectionchange_eng_type)

        minYear = int(year1)
        maxYear = int(year2)

        self.spinBox_year1.setMinimum(minYear)
        self.spinBox_year1.setMaximum(maxYear + 1)
        self.spinBox_year1.setValue(minYear)
        self.spinBox_year1.valueChanged.connect(self.valuechange_year1)

        self.spinBox_year2.setMinimum(minYear)
        self.spinBox_year2.setMaximum(maxYear + 1)
        self.spinBox_year2.setValue(maxYear)
        self.spinBox_year2.valueChanged.connect(self.valuechange_year2)

        self.addToolBar(NavigationToolbar(self.MplWidget_PKB.canvas, self))
        self.addToolBar(NavigationToolbar(self.MplWidget_engine.canvas, self))

        self.update_graph_PKB()
        self.update_graph_engine()

        self.pdfButton.clicked.connect(self.generate_pfd)

    #will only work on unix, for convert look at README.md
    def generate_pfd(self, ideself):
        self.MplWidget_engine.grab().save("/tmp/engine.jpg")
        self.MplWidget_PKB.grab().save("/tmp/pkb.jpg")
        os.system("convert /tmp/engine.jpg /tmp/pkb.jpg raport.pdf")
        print("generating pdgf")

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
        global year1
        if self.spinBox_year1.value() < 1990:
            year1 = 1990
        else:
            if self.spinBox_year1.value() < year2:
                year1 = self.spinBox_year1.value()

        update_pkb_values()
        self.update_graph_PKB()
        self.update_graph_engine()

    def valuechange_year2(self):
        global year2
        if self.spinBox_year2.value() > 2018:
            year2 = 2018
        else:
            if self.spinBox_year2.value() > year1:
                year2 = self.spinBox_year2.value()

        update_pkb_values()
        self.update_graph_PKB()
        self.update_graph_engine()

    def update_graph_PKB(self, country=country_PKB):
        global year1, year2, PKB_data
        year_start=year1
        year_stop=year2

        # narazie bierze 1 liste z PKB_data
        country_PKB_data = PKB_data[self.comboBox_country_PKB.currentIndex()]
        # t = np.linspace(year_start, year_stop, (year_stop - year_start) + 1)
        t = []
        for i in range(year_start, year_stop+1):
            t.append(i)

        print(t)
        print(PKB_data[0])

        locator = matplotlib.ticker.MultipleLocator(2)
        formatter = matplotlib.ticker.StrMethodFormatter("{x:.0f}")


        self.MplWidget_PKB.canvas.axes.clear()

        self.MplWidget_PKB.canvas.axes.plot(t, country_PKB_data)
        self.MplWidget_PKB.canvas.axes.xaxis.set_major_locator(locator)
        self.MplWidget_PKB.canvas.axes.xaxis.set_major_formatter(formatter)
        self.MplWidget_PKB.canvas.axes.legend(('year', 'PKB'), loc='upper right')
        self.MplWidget_PKB.canvas.axes.set_title('Country PKB')
        self.MplWidget_PKB.canvas.draw()

    def update_graph_engine(self, country=country_PKB, engine_type = type_of_engine):
        global year1, year2
        year_start=year1
        year_stop=year2
        # here im not sure of engine data structure

        # data = engine_data[country][engine_type]

        locator = matplotlib.ticker.MultipleLocator(2)
        formatter = matplotlib.ticker.StrMethodFormatter("{x:.0f}")

        t = np.linspace(year_start, year_stop, (year_stop - year_start) + 1)
        data = np.linspace(year_start, year_stop, (year_stop - year_start) + 1)
        self.MplWidget_engine.canvas.axes.clear()
        self.MplWidget_engine.canvas.axes.plot(t, data)
        self.MplWidget_engine.canvas.axes.xaxis.set_major_locator(locator)
        self.MplWidget_engine.canvas.axes.xaxis.set_major_formatter(formatter)
        self.MplWidget_engine.canvas.axes.legend(('year', 'amount of cars'), loc='upper right')
        self.MplWidget_engine.canvas.axes.set_title('Cars bought by engine type')
        self.MplWidget_engine.canvas.draw()

def main():
    global year1, year2, countries
    app = QApplication([])
    window = MatplotlibWidget(countries)
    window.show()
    app.exec_()

if __name__ == "__main__":
    sys.exit(main())
