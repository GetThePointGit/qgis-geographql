from qgis.PyQt import QtWidgets, uic, QtWebKitWidgets
#QtWebEngineWidgets
from qgis.PyQt.QtWidgets import QSizePolicy
from qgis.PyQt.QtCore import pyqtSignal, QUrl, pyqtSlot, QObject, Qt
from qgis.PyQt.QtNetwork import QNetworkProxyFactory
from qgis.PyQt.QtWebKit import QWebSettings
from qgis.core import QgsVectorLayer, QgsProject, QgsFeature, QgsGeometry, QgsPointXY

import os
import json




class PythonAPI(QObject):

    def __init__(self, callback_new_data):
        super().__init__()
        self.callback_new_data = callback_new_data

    @pyqtSlot('QVariantMap')
    def new_data(self, obj):
        self.callback_new_data(obj)


class QueryBuilderWidget(QtWidgets.QDockWidget):
    closingWidget = pyqtSignal()

    def __init__(self, parent=None, iface=None):

        super(QueryBuilderWidget, self).__init__(parent)
        self.iface = iface

        self._polygons = QgsVectorLayer(
            "polygon?crs={0}&field=name:string(20)".format(28992),
            "building",
            "memory")

        self._points = QgsVectorLayer(
            "point?crs={0}&field=ahn:double".format(28992),
            "point",
            "memory")

        QgsProject.instance().addMapLayer(
            self._polygons,
            False)

        QgsProject.instance().addMapLayer(
            self._points,
            False)

        root = QgsProject.instance().layerTreeRoot()
        group = root.addGroup('GeoGraphQL')
        group.addLayer(self._points)
        group.addLayer(self._polygons)

        self.setup_ui()

        self.api = PythonAPI(self.on_new_data)
        self.frame = self.web_view.page().mainFrame()
        self.frame.javaScriptWindowObjectCleared.connect(self.load_api)

        QNetworkProxyFactory.setUseSystemConfiguration(True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.DnsPrefetchEnabled, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptEnabled, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.OfflineStorageDatabaseEnabled, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.AutoLoadImages, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.LocalStorageEnabled, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.PrivateBrowsingEnabled, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        # url = "https://gateway.geographql.com/"
        url = 'http://localhost:4005/console'
        # url = 'http://localhost:3000/'
        url = QUrl(url)

        file_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'build', 'index.html')

        url = QUrl.fromLocalFile(file_path)

        self.web_view.load(url)

    def on_unload(self):
        self.frame.javaScriptWindowObjectCleared.disconnect(self.load_api)

    def load_api(self):
        print('load_api')
        self.frame.addToJavaScriptWindowObject('pyapi', self.api)

    def add_point(self, feature):
        self._points.dataProvider().addFeatures([feature])
        self._points.updateExtents()

    def add_polygon(self, feature):
        self._polygons.dataProvider().addFeatures([feature])
        self._polygons.updateExtents()

    def make_feature_recursive(self, key, value):

        if value.get("__typename"):


            if value.get("__typename") == "Point" and value.get('x') is not None and value.get('y') is not None:
                feat = QgsFeature(self._points.fields())
                geom = QgsGeometry.fromPointXY(QgsPointXY(value.get('x'), value.get('y')))
                feat.setGeometry(geom)
                feat.setAttribute('ahn', value.get('ahn'))
                self.add_point(feat)
            elif value.get("__typename") == "Building" and type(value.get('geom') == dict):
                feat = QgsFeature(self._polygons.fields())
                geom = QgsGeometry.fromWkt(value.get('geom'))
                feat.setGeometry(geom)
                feat.setAttribute('name', value.get('name'))
                self.add_polygon(feat)

        for k, v in value.items():

            if type(v) == list:
                for list_v in v:
                    if type(list_v) == dict:
                        self.make_feature_recursive("{}-{}".format(key, k), list_v)
            elif type(v) == dict:
                self.make_feature_recursive("{}-{}".format(key, k), v)

    def on_new_data(self, obj):
        print(obj)
        if 'data' in obj:
            for key, value in obj['data'].items():
                if type(value) == dict:
                    self.make_feature_recursive(key, value)

        extent = self._points.extent()
        extent.combineExtentWith(self._polygons.extent())
        extent.scale(1.1)

        canvas = self.iface.mapCanvas()
        canvas.setExtent(extent)

    def setup_ui(self):

        self.dock_widget_content = QtWidgets.QWidget(self)
        self.setObjectName("graphqlDockWidget")
        self.dock_widget_content.setObjectName("graphqlMainWidget")

        self.main_vlayout =  QtWidgets.QVBoxLayout(self.dock_widget_content)
        self.dock_widget_content.setLayout(self.main_vlayout)

        #self.web_view = QtWebEngineWidgets.QWebEngineView(self.dock_widget_content)
        self.web_view = QtWebKitWidgets.QWebView(self.dock_widget_content)
        self.main_vlayout.addWidget(self.web_view)

        self.button_bar = QtWidgets.QHBoxLayout(self.dock_widget_content)
        self.load_button = QtWidgets.QPushButton(self.dock_widget_content)
        self.refresh_button = QtWidgets.QPushButton(self.dock_widget_content)
        spacer = QtWidgets.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.button_bar.addWidget(self.load_button)
        self.button_bar.addSpacerItem(spacer)
        self.button_bar.addWidget(self.refresh_button)

        self.main_vlayout.addLayout(self.button_bar)

        self.setWidget(self.dock_widget_content)

        self.setWindowTitle("GeoGraphQL")
        self.load_button.setText("Laad data")

        self.refresh_button.setText("Refresh")

