# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginIGN
                                 A QGIS plugin
 Plugin para cargar los servicios del IGN / CNIG
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-08-24
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Alejandro Garcia Barroso
        email                : alejandro.garcia@cnig.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
import json

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geocoder_dialog.ui'))


class GeocoderDialog(QtWidgets.QDialog, FORM_CLASS):
        
    def __init__(self, parent=None):
        """Constructor."""
        self.valoresTabla =["comunidadAutonoma","province","muni","poblacion","postalCode","tip_via","address","portalNumber"]
        super(borrarDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


    def doModal(self,addresses):
        self.populateTable(addresses)
        self.show()
        self.return_value = self.exec_()
        return self.return_value
    
    
    def populateTable(self,addresses):
        self.tableWidget.setColumnCount(len(self.valoresTabla))
        self.tableWidget.setRowCount(len(addresses))
        self.tableWidget.setHorizontalHeaderLabels(self.valoresTabla)
        self.tableWidget.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
              
        row = 0
        for address in addresses:
            col = 0
            for key in self.valoresTabla:
                item = QTableWidgetItem(address[key])
                flags = item.flags()
                flags ^= 2
                item.setFlags(flags)
                self.tableWidget.setItem(row,col,item)
                col += 1
            row += 1
        
        