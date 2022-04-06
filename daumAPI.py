# -*- coding: utf-8 -*-
import os,sys
ParentDir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
if not ParentDir in sys.path:
    sys.path.append(ParentDir)

from qgis.PyQt.QtWidgets import (QAction, QFileDialog, QMessageBox)
from qgis.PyQt.QtGui import (QIcon, QColor, QFont)
from qgis.PyQt import (uic)
from qgis.PyQt.QtWidgets import (QDialog)
from qgis.PyQt.QtCore import (QSettings, QTranslator, qVersion, QCoreApplication, Qt, QVariant)
from qgis.core import (QgsRectangle, QgsVectorFileWriter, QgsCoordinateReferenceSystem, QgsVectorLayer, \
                       QgsLayerTreeLayer, QgsProject, QgsTask, QgsApplication, QgsMessageLog, QgsFields, QgsField,
                       QgsWkbTypes, QgsFeature, QgsPointXY, QgsGeometry, QgsCoordinateTransform, QgsSimpleMarkerSymbolLayerBase, QgsPalLayerSettings,QgsTextFormat, QgsTextBufferSettings, QgsVectorLayerSimpleLabeling)
from qgis.utils import Qgis
from .apps.QgsMapPointool import PointTool

import json,os ,csv
import urllib
import urllib.request
import webbrowser 

#from ui.mainDialog import Ui_kakaoDia

QDialogClass, _= uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/mainDialog.ui'))

# Import ui file
class DaumAPIDialog(QDialog, QDialogClass):
    def __init__(self, parent=None):
        # """Constructor."""
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)
        super(DaumAPIDialog, self).__init__(parent)
        self.setupUi(self)


class daumAPI:
    """QGIS Plugin Starting"""
    
    def __init__(self, iface):
    
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DaumApi_{}.qm'.format(locale))
            
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
                
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&KaKaoAPi')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'KaKaoAPi')
        self.toolbar.setObjectName(u'KaKaoAPi')
        
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DaumAPI', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):

        # Create the dialog (after translation) and keep reference

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action
        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Kakao Map'),
                action)
            self.iface.removeToolBarIcon(action)
            # remove the toolbar
        del self.toolbar
        
        
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = '::/plugins/DaumAPI_Tool/icon/dmApi.svg'
        self.clickApi=self.add_action(
            icon_path,
            text=self.tr(u'Kakao Map'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.dlg = DaumAPIDialog()
        self.dlg.jusoSearch.clicked.connect(self.jusoSearch)
        self.dlg.spotClick.clicked.connect(self.spotClick)
        self.dlg.ShowRoadView.clicked.connect(self.ShowRoadView)
        self.dlg.fileSel.clicked.connect(self.fileSel)
        self.dlg.MultiSavePathSel.clicked.connect(self.MultiSavePathSel)
        self.dlg.MultiSaveRun.clicked.connect(self.MultiSaveRun)
        self.dlg.saveImg.clicked.connect(self.saveImg)
        
        self.clickApi.setCheckable(True)
        self.clickApi.setEnabled(True)
        
        self.canvas = self.iface.mapCanvas()

    def mouseClick(self):
        try:
            self.iface.setActiveLayer(self.canvas.layers()[0])
        except:
            pass
        self.canvas.setMapTool(self.toolMouseClick)
        self.clickApi.setChecked(True)

    def run(self):
        #self.dlg.coordinate.setDisabled(True)
        self.dlg.show()
        
    def jusoSearch(self):
        #print('this is jusoSearch')
        client_id = self.dlg.apiCode.text()
        jusoInput = self.dlg.jusoInput.text()
        #QMessageBox.information(None, "주소입력값", jusoInput)

        encJusoText = urllib.parse.quote(jusoInput[:-1])
        url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + encJusoText 
        
        #QMessageBox.information(None, "url입력값", url)
        
        request = urllib.request.Request(url)
        request.add_header("Authorization","KakaoAK " + client_id)
        response = urllib.request.urlopen(request)
        response_body = response.read()
        json_addr = response_body.decode('utf-8')
        cd_cnt = json.loads(json_addr)['meta']['total_count']
        lineCnt = 1
        #setprogressbar
        progreIndex = int(1/1*100)
        self.dlg.progressBar.setValue(progreIndex)
        #get Coordinates from ComboBox
        self.strCrsFullId = self.dlg.mQgsProjectionSelectionWidget.crs().authid()
        
        if(cd_cnt>=1):
            y_coord = json.loads(json_addr)['documents'][0]['y']
            x_coord = json.loads(json_addr)['documents'][0]['x']
            y_coord = float(y_coord)
            x_coord = float(x_coord)
            
            #strCrsFullId = self.dlg.mQgsProjectionSelectionWidget.crs().authid()
            #QMessageBox.information(None, "crs값", strCrsFullId)
            
            transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'), QgsCoordinateReferenceSystem(self.strCrsFullId), QgsProject.instance())
            coord = transform.transform(x_coord, y_coord)
            self.y_coord = coord.y()
            self.x_coord = coord.x()
            xy = 'x:' + str(self.x_coord) + ' y:' + str(self.y_coord)
            #QMessageBox.information(None, "xy반환값", xy)
        else:
            QMessageBox.information(None, "error", 'no inputs')
            
        #add point layer in memory and zoom to point
        vlyr = QgsVectorLayer("Point", jusoInput, "memory")
        vlpr = vlyr.dataProvider()
        vlpr.addAttributes([QgsField("주소", QVariant.String)])
        vlyr.updateFields()
        singlefeat = QgsFeature()
        singlefeat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.x_coord,self.y_coord)))
        singlefeat.setAttributes([jusoInput])
        vlpr.addFeature(singlefeat)
        vlyr.updateExtents()

        self.epsgCode = self.strCrsFullId.split(":")[1]#split "EPSG:51XX" to ["EPSG", "51xx"]
        vlyr.setCrs(QgsCoordinateReferenceSystem(int(self.epsgCode)))
        QgsProject.instance().addMapLayer(vlyr)
        
        newExtent = vlyr.extent()
        
        #set text Label and format
        layer_settings  = QgsPalLayerSettings()
        text_format = QgsTextFormat()
        text_format.setFont(QFont("돋움체", 12))
        text_format.setSize(12)
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor("white"))
        text_format.setBuffer(buffer_settings)
        layer_settings.setFormat(text_format)
        layer_settings.fieldName = "주소"
        layer_settings.placement = 2
        layer_settings.enabled = True
        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        vlyr.setLabelsEnabled(True)
        vlyr.setLabeling(layer_settings)
        
        #set symbol size and color,
        vlyr.renderer().symbol().setSize(6)
        vlyr.renderer().symbol().setColor(QColor("yellow"))
        vlyr.renderer().symbol().symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Star)
        vlyr.triggerRepaint()
        
        #set extents and scale
        self.canvas.zoomScale(1000) #set zoomScale to 1: 1000
        self.canvas.setExtent(newExtent)
        self.canvas.refresh()
        
        #self.dlg.jusoInput.clear()

    def saveImg(self):
        svImgPath = QFileDialog.getSaveFileName(parent=None, caption=u'inserts fileName', filter='jpg files(*.jpg)')
        self.canvas.saveAsImage( svImgPath[0] )

    def ShowRoadView(self):
        #print('this is showRoadView')
        jusoForRoad = self.dlg.jusoInput.text()
        locatForRoad = self.dlg.coordinate.text()
        actual_crs = QgsCoordinateReferenceSystem(self.strCrsFullId)
        crsDest = QgsCoordinateReferenceSystem("EPSG:4326")
        if jusoForRoad  != "" :
            xform = QgsCoordinateTransform(actual_crs, crsDest,QgsProject.instance())
            wgsPt1 = xform.transform(QgsPointXY(self.x_coord, self.y_coord))
            #QMessageBox.information(None, "xy반환값", str(wgsPt1.x()))
            lat, lon = str(wgsPt1.y()), str(wgsPt1.x())
            roadvieAddress = 'https://map.kakao.com/link/roadview/' + lat+ ','+ lon
            webbrowser.open_new(roadvieAddress)
            
        elif locatForRoad is not None:
            xform = QgsCoordinateTransform(actual_crs, crsDest,QgsProject.instance())
            cooridLoc = self.dlg.coordinate.text().split(',')
            loc_X, loc_Y  =cooridLoc[0], cooridLoc[1]
            locPt1 = xform.transform(QgsPointXY(float(loc_X), float(loc_Y)))
            #QMessageBox.information(None, "xy반환값", str(locPt1.x()))
            #Output x -> lon, y->lat
            lat, lon = str(locPt1.y()), str(locPt1.x())
            roadvieAddress = 'https://map.kakao.com/link/roadview/' + lat+ ','+ lon
            webbrowser.open_new(roadvieAddress)
            
        else:
            gabage = 'nothing'

    def spotClick(self):
        #print('this is spotClick')
        self.coord_X,self.coord_Y, = 0, 0
        mapTool = PointTool(self.canvas, parent=self)
        self.canvas.setMapTool(mapTool)
        self.dlg.jusoInput.clear()
        #QMessageBox.information(None, "juso값", self.dlg.jusoInput.text())
        
    def fileSel(self):
        txtFilePath = QFileDialog.getOpenFileName(parent=None, caption=u'Please select text file', filter='Text files(*.txt *.csv)')
        self.dlg.MultiJusoPath.setText(txtFilePath[0])
        
    def MultiSavePathSel(self):
        svFilePath = QFileDialog.getSaveFileName(parent=None, caption=u'save file name', filter='shp files(*.shp)')
        self.dlg.MultiSavePath.setText(svFilePath[0])
        
    def MultiSaveRun(self):
        client_id = self.dlg.apiCode.text()
        MjusoTxt = self.dlg.MultiJusoPath.text()
        MjusoShpPat = self.dlg.MultiSavePath.text()
        MjusoErrTxt = MjusoShpPat.split('.')[0] + '_error.txt'
        ff = open(MjusoErrTxt, 'w')
        readJusoTxt = open(MjusoTxt, 'r', encoding='utf-8')
        lines = readJusoTxt.readlines()
        lineCnt = 0
        totCnt = len(lines)
        ff.write('result, address, x_coord, y_coord \n')
        
        #set vectorlayer properties
        vlyr = QgsVectorLayer("Point", 'jusoToShp', 'memory')
        vlpr = vlyr.dataProvider()
        vlpr.addAttributes([QgsField("주소", QVariant.String),  QgsField("ID", QVariant.String)])
        vlyr.updateFields()
        
        #set features
        multiFeat = QgsFeature()
        
        for line in lines:
            #QMessageBox.information(None, "주소값", line)
            encText = urllib.parse.quote(line[:-1])
            url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + encText
            request = urllib.request.Request(url)
            request.add_header("Authorization","KakaoAK " + client_id)
            response = urllib.request.urlopen(request)
            response_body = response.read()
            json_addr = response_body.decode('utf-8')
            cd_cnt = json.loads(json_addr)['meta']['total_count']
            #QMessageBox.information(None, "cd_cnt", str(cd_cnt) )
            lineCnt += 1
            #set progress bar values
            progre = int(lineCnt/totCnt*100)
            self.dlg.progressBar.setValue(progre)
            if(cd_cnt>=1):
                y_coord = json.loads(json_addr)['documents'][0]['y']
                x_coord = json.loads(json_addr)['documents'][0]['x']
                y_coord = float(y_coord)
                x_coord = float(x_coord)
                strCrsFullId = self.dlg.mQgsProjectionSelectionWidget.crs().authid()
                transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'), QgsCoordinateReferenceSystem(strCrsFullId), QgsProject.instance())
                coord = transform.transform(x_coord, y_coord)
                y_coord = coord.y()
                x_coord = coord.x()
                #QMessageBox.information(None, "주소값", str(x_coord) )
                #add point feature in to Vector layer
                multiFeat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x_coord,y_coord)))
                multiFeat.setAttributes([line,str(lineCnt) ])
                vlpr.addFeature(multiFeat)
            else:
                ff.write('fail(there is no address)| ' + line + '| | \n')

        #update vectorlayer
        vlyr.updateExtents()
        epsgCode = strCrsFullId.split(":")[1]#split "EPSG:51XX" to ["EPSG", "51xx"]
        vlyr.setCrs(QgsCoordinateReferenceSystem(int(epsgCode)))
        QgsProject.instance().addMapLayer(vlyr)
        newExtent = vlyr.extent()
        
        #update vector layer style
        vlyr.renderer().symbol().setSize(6)
        vlyr.renderer().symbol().setColor(QColor("yellow"))
        vlyr.renderer().symbol().symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Star)
        vlyr.triggerRepaint()
        
        #set extents and scale
        self.canvas.zoomScale(1000) #set zoomScale to 1: 1000
        self.canvas.setExtent(newExtent)
        self.canvas.refresh()
        
        #output Vector layers
        QgsVectorFileWriter.writeAsVectorFormat(vlyr, MjusoShpPat, "UTF-8", vlyr.crs(), "ESRI Shapefile")