from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui
import time
import os
import matplotlib

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import numpy as np
import sys
import requests
import xmltodict
import random
import math

# GLOBAL VARIABLES - FOR NOW
year1 = 2000
year2 = 2013
countries_array = ['DE', 'ES', 'FR', 'IT', 'PL']
PKB_data = []
ENGINE_data= []
engine_type = 'PET'
engine_size = 'CC_GE2000'

engine_type_array = ['PET', 'DIE']
engine_type_array_nice_titles = ['Petroleum', 'Diesel']
engine_size_array = ['CC_LT1400', 'CC1400-1999', 'CC_GE2000', 'TOTAL']
engine_size_array_nice_titles = ['0 - 1400', '1400-1999', '2000 - 6000', 'Total']

# Engine size: CC_LT1400, CC1400-1999, CC_GE2000
# ENGINE TYPE: PET, DIE, TOTAL ( z total cos dziwne dane sciaga )

CARMOT_URL = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/datastructure/ESTAT/DSD_road_eqr_carmot"
url = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/nama_10_gdp/.CP_MEUR.B1GQ."+"DE+FR+IT+GR+PL?startPeriod=2000&endPeriod=2013"
url_engines = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/road_eqs_carmot/.."+engine_type+"."+engine_size+".DE+FR+IT+PL+FR+ES?startPeriod=2010&endPeriod=2015"

class Data:
    def __init__(self, name):
        self.name = name
        self.years = []
        self.values = []

    def addEntry(self, year, value):
        self.years.append(year)
        self.values.append(value)

def getFont(size, bold):
    font = QtGui.QFont()
    font.setPointSize(size)
    font.setBold(bold)
    return font

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
    countries = "DE+FR+IT+PL+FR+ES"
    url = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/nama_10_gdp/.CP_MEUR.B1GQ."+countries+"?startPeriod="+str(start_year)+"&endPeriod="+str(end_year)
    r = requests.get(url)
    doc = xmltodict.parse(r.content)
    result = parseDictionary(doc)
    return result

def update_pkb_values():
    global PKB_data
    PKB_data.clear()
    data = get_pkb_values()
    for country in data:
        tmp_values = []
        for value in country.values:
            tmp_values.append(int(float(value))/1000)
        PKB_data.append(tmp_values)

def get_engine_values():
    global year1, year2, engine_type, engine_size
    start_year = year1
    end_year = year2
    countries = "DE+FR+IT+PL+FR+ES"
    url_engines = "http://ec.europa.eu/eurostat/SDMX/diss-web/rest/data/road_eqs_carmot/.."+engine_type+"."+engine_size+"."+countries+"?startPeriod="+str(start_year)+"&endPeriod="+str(end_year)
    r = requests.get(url_engines)
    doc = xmltodict.parse(r.content)
    result = parseDictionary(doc)
    return result

def update_engine_values():
    global ENGINE_data
    ENGINE_data.clear()
    data = get_engine_values()
    for country in data:
        tmp_values = []
        for value in country.values:
            tmp_value = 0
            try:
                tmp_value = float(value)
            except ValueError:
                tmp_value = 0
            tmp_values.append(tmp_value/10000)
        ENGINE_data.append(tmp_values)

class MatplotlibWidget(QMainWindow):
    def __init__(self, data):
        global PKB_data, countries_array, year1, year2, engine_type_array, engine_size_array
        QMainWindow.__init__(self)

        loadUi("1.ui", self)
        self.setWindowTitle("")
        self.carMotData = data

        update_pkb_values()
        update_engine_values()

        self.comboBox_country_PKB.addItems(countries_array)
        self.comboBox_country_PKB.currentIndexChanged.connect(self.selectionchange_PKB)
        self.comboBox_country_PKB_2.addItems(countries_array)
        self.comboBox_country_PKB_2.currentIndexChanged.connect(self.selectionchange_PKB_2)
        self.comboBox_country_PKB_2.setCurrentIndex(1)

        self.comboBox_country_engines.addItems(countries_array)
        self.comboBox_country_engines.currentIndexChanged.connect(self.selectionchange_eng_country)
        self.comboBox_country_engines_2.addItems(countries_array)
        self.comboBox_country_engines_2.currentIndexChanged.connect(self.selectionchange_eng_country_2)
        self.comboBox_country_engines_2.setCurrentIndex(1)
        self.comboBox_engine_type.addItems(engine_type_array_nice_titles)
        self.comboBox_engine_type.currentIndexChanged.connect(self.selectionchange_eng_type)
        self.comboBox_engine_size.addItems(engine_size_array_nice_titles)
        self.comboBox_engine_size.currentIndexChanged.connect(self.selectionchange_eng_size)

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
        self.labelTimeInterval.setFont(getFont(16, False))
        self.labelMainTitle.setFont(getFont(24, True))
        self.labelSubtitle.setFont(getFont(20, False))

    def generate_pfd(self, ideself):
        global year1, year2
        os.system("touch /tmp/text.md")
        os.system("echo \"\" > /tmp/text.md")
        os.system("echo \"# Report\" >> /tmp/text.md")
        os.system("echo \"## Genated for years:" + str(year1) + " - " + str(year2) + " \" >> /tmp/text.md")
        os.system("echo \"## Countries in report: " + self.comboBox_country_engines.currentText() + ", " + self.comboBox_country_PKB.currentText() + ", " + self.comboBox_country_PKB_2.currentText() + " \" >> /tmp/text.md")
        os.system("markdown-pdf /tmp/text.md")
        self.MplWidget_engine.grab().save("/tmp/engine.jpg")
        self.MplWidget_PKB.grab().save("/tmp/pkb.jpg")
        os.system("convert /tmp/text.pdf /tmp/engine.jpg /tmp/pkb.jpg raport.pdf")

    def selectionchange_PKB(self, index):
        self.update_graph_PKB()

    def selectionchange_PKB_2(self, index):
        self.update_graph_PKB()

    def selectionchange_eng_country(self, index):
        self.update_graph_engine()

    def selectionchange_eng_country_2(self, index):
        self.update_graph_engine()

    def selectionchange_eng_type(self, index):
        global engine_type, engine_type_array
        engine_type = engine_type_array[index]
        update_engine_values()
        self.update_graph_engine()

    def selectionchange_eng_size(self, index):
        global engine_size, engine_size_array
        engine_size = engine_size_array[index]
        update_engine_values()
        self.update_graph_engine()

    def valuechange_year1(self):
        global year1
        if self.spinBox_year1.value() < 1990:
            year1 = 1990
        else:
            if self.spinBox_year1.value() < year2:
                year1 = self.spinBox_year1.value()

        update_engine_values()
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

        update_engine_values()
        update_pkb_values()
        self.update_graph_PKB()
        self.update_graph_engine()

    def update_graph_PKB(self):
        global year1, year2, PKB_data
        year_start=year1
        year_stop=year2

        country_PKB_data = PKB_data[self.comboBox_country_PKB.currentIndex()]
        country_PKB_data_2 = PKB_data[self.comboBox_country_PKB_2.currentIndex()]
        r_country_PKB_data = list(reversed(country_PKB_data))
        r_country_PKB_data_2 = list(reversed(country_PKB_data_2))

        t = []
        for i in range(year_start, year_stop+1):
            t.append(i)

        pkb_title1 = self.comboBox_country_PKB.currentText()
        pkb_title2 = self.comboBox_country_PKB_2.currentText()

        locator = matplotlib.ticker.MultipleLocator(2)
        formatter = matplotlib.ticker.StrMethodFormatter("{x:.0f}")
        self.MplWidget_PKB.canvas.axes.clear()
        self.MplWidget_PKB.canvas.axes.plot(t, r_country_PKB_data)
        self.MplWidget_PKB.canvas.axes.plot(t, r_country_PKB_data_2)
        self.MplWidget_PKB.canvas.axes.xaxis.set_major_locator(locator)
        self.MplWidget_PKB.canvas.axes.xaxis.set_major_formatter(formatter)
        self.MplWidget_PKB.canvas.axes.set_xlabel('Years')
        self.MplWidget_PKB.canvas.axes.set_ylabel('PKB (in thousands)')
        self.MplWidget_PKB.canvas.axes.legend((pkb_title1, pkb_title2), loc='upper right')
        self.MplWidget_PKB.canvas.axes.set_title(pkb_title1 + ', ' + pkb_title2 + ' PKB')
        self.MplWidget_PKB.canvas.draw()

    def update_graph_engine(self):
        global year1, year2, ENGINE_data
        year_start=year1
        year_stop=year2

        country_ENGINE_data = ENGINE_data[self.comboBox_country_engines.currentIndex()]
        country_ENGINE_data_2 = ENGINE_data[self.comboBox_country_engines_2.currentIndex()]
        r_country_ENGINE_data = list(reversed(country_ENGINE_data))
        r_country_ENGINE_data_2 = list(reversed(country_ENGINE_data_2))
        t = []
        for i in range(year_start, year_stop+1):
            t.append(i)

        engine_title1 = self.comboBox_country_engines.currentText()
        engine_title2 = self.comboBox_country_engines_2.currentText()

        engine_type_title = ''
        engine_type_title = self.comboBox_engine_type.currentText()

        formatter = matplotlib.ticker.StrMethodFormatter("{x:.0f}")
        locator = matplotlib.ticker.MultipleLocator(2)
        self.MplWidget_engine.canvas.axes.clear()
        self.MplWidget_engine.canvas.axes.plot(t, r_country_ENGINE_data)
        self.MplWidget_engine.canvas.axes.plot(t, r_country_ENGINE_data_2)
        self.MplWidget_engine.canvas.axes.xaxis.set_major_locator(locator)
        self.MplWidget_engine.canvas.axes.xaxis.set_major_formatter(formatter)
        self.MplWidget_engine.canvas.axes.set_xlabel('Years')
        self.MplWidget_engine.canvas.axes.set_ylabel('Cars (in ten thousands)')
        self.MplWidget_engine.canvas.axes.legend((engine_title1, engine_title2), loc='upper right')
        self.MplWidget_engine.canvas.axes.set_title(engine_type_title + ' cars bought in ' + engine_title1 + ', ' + engine_title2)
        self.MplWidget_engine.canvas.draw()

def main():
    global year1, year2, countries_array
    app = QApplication([])
    window = MatplotlibWidget(countries_array)
    window.show()
    app.exec_()

if __name__ == "__main__":
    sys.exit(main())
