import os,sys,csv
cur_dir = os.path.dirname(os.path.realpath(__file__))

from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsMapToolPan, QgsMapToolEmitPoint, QgsMapTool
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QMenu, QMessageBox
from qgis.PyQt.QtGui import QIcon, QMovie,QColor
from qgis.core import Qgis as QGis, QgsProject, QgsVectorLayer,QgsGeometry,QgsPoint,QgsPointXY

class PointTool(QgsMapTool):   
    def __init__(self, canvas,parent=None):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas    
        self.parent = parent
        
    def canvasPressEvent(self, event):
        if event.button() == None:
            event_alert = QMessageBox.information(self, '클릭오류', "클릭한 지점이 없음.", QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Ok)
        elif event.button() == Qt.LeftButton:
            realCoordinates = QgsGeometry.fromPointXY(self.canvas.getCoordinateTransform().toMapCoordinates(event.pos().x(), event.pos().y()))
            plainCoordi = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos().x(), event.pos().y())
            coordiText = str(round(plainCoordi.x(),4)) + ',' + str(round(plainCoordi.y(), 4))
            #self.parent.coord_X,self.parent.coord_Y, = round(plainCoordi.x(),4), round(plainCoordi.y(),4)
            self.parent.dlg.coordinate.setText(coordiText)
        else:
            print('you just Click Right Button')
