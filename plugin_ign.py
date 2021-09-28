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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication,QSize,QObject
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction,QToolBar,QCheckBox,QLabel,QStatusBar,QMenu,QToolButton,QComboBox
from qgis.core import QgsProject,QgsRectangle,QgsRasterLayer

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .plugin_ign_dialog import PluginIGNDialog
import os.path
from qgis._core import QgsRasterLayer
from builtins import *
from .wmts import Wmts
from .wms import Wms
from .geocoder import Geocoder
from .utils import Utils
from qgis.utils import iface

class PluginIGN:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PluginIGN_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.mainAction = None
        self.toolBars = []
        self.toolButtons = []
        self.menus = []
        self.services = []
        self.cmbbox = None
        self.about = None  
        self.menu = self.tr(u'&Plugin IGN ')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PluginIGN', message)

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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        self.mainAction = QAction(icon, text, parent)
        self.mainAction.triggered.connect(callback)
        self.mainAction.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(self.mainAction)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                self.mainAction)

        return self.mainAction

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""


        wmsFilePath=self.plugin_dir +'/resources/wms.txt'
        wmtsFilePath=self.plugin_dir +'/resources/wmts.txt'
        self.icon_path = ':/plugins/plugin_ign/images/150Aniversario.png'
        self.iconPathWms = ':/plugins/plugin_ign/images/wms.png'
        self.iconPathIGN = ':/plugins/plugin_ign/images/150Aniversario.png'
        self.iconPathTopo = ':/plugins/plugin_ign/images/spain_topo.png'
                        
        self.add_action(
            self.icon_path,
            text=self.tr(u'IGN CNIG'),
            callback=self.run,
            parent=self.iface.mainWindow())

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(25,25))
        self.iface.mainWindow().addToolBar(toolbar)
        self.toolBars.append(toolbar) 
           
        self.cmbbox = QComboBox()
        self.cmbbox.setFixedSize(QSize(250,25))
        self.cmbbox.setEditable(True)
        self.cmbbox.setToolTip("Buscador de lugares tanto por nombres como por coordenadas,\nen este último caso el formato será como el siguiente ejemplo: \nEPSG:4326 -3.65 40.32")
        self.cmbbox.activated.connect(self.geocoder) # Press intro and select combo value      

        mainMenu = QMenu()          
        mainMenu.setIcon(QIcon(self.iconPathIGN)) 
        
        wmsMenu = self.createQmenu("Sevicios WMS", self.iconPathWms)
        wmtsMenu = self.createQmenu("Sevicios WMTS", self.iconPathWms)
       
        wmsServices = self.convertServicesFromFilesIntoClasses(wmsFilePath,"wms")
        wmtsServices = self.convertServicesFromFilesIntoClasses(wmtsFilePath,"wmts")
        
        self.putServicesIntoQmenu(wmsServices, wmsMenu)
        self.putServicesIntoQmenu(wmtsServices, wmtsMenu)
          
        mainMenu.addMenu(wmsMenu)  
        mainMenu.addMenu(wmtsMenu) 
         
        self.menus.append((mainMenu.parentWidget,mainMenu))
        self.menus.append((wmsMenu.parentWidget,wmsMenu))
        self.menus.append((wmtsMenu.parentWidget,wmtsMenu))
 
        testToolButton = QToolButton()
        testToolButton.setPopupMode(QToolButton().MenuButtonPopup)
        testToolButton.setIcon(QIcon(self.iconPathIGN))
        testToolButton.setMenu(mainMenu)
         
        self.toolButtons.append((testToolButton.parentWidget(),testToolButton))
         
        self.actions.append((toolbar,toolbar.addWidget(self.cmbbox)))
        self.actions.append((toolbar,toolbar.addWidget(testToolButton)))
        
        # will be set False in run()
        self.first_start = True    

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
#         for action in self.actions:
#             self.iface.removePluginMenu(
#                 self.tr(u'&Plugin IGN '),
#                 action)
#             self.iface.removeToolBarIcon(action)
            
        for parent, action in self.actions:            
             parent.removeAction(action)                    
        self.actions = []
                
        for parent,menu in self.menus:
            menu.clear()
        self.menus = []              

        for toolbar in self.toolBars:
            parent = toolbar.parentWidget()
            parent.removeToolBar(toolbar)
            print("Toolbar remove", toolbar.windowTitle())
            del toolbar
        self.toolBars = []
                
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu(self.tr(u'&Plugin IGN'),self.mainAction)        
        self.iface.removeToolBarIcon(self.mainAction)
           
        QgsProject.instance().clear()

    def run(self):

        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = PluginIGNDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def createQmenu(self,menuName, menuIcon):                
        qmenu = QMenu()   
        qmenu.setIcon(QIcon(menuIcon))
        qmenu.setTitle(menuName)         
        return qmenu
    
    def geocoder(self):         
        #crear clase geocoder y desde alli llamar a la ventana de seleccion si es necesario           
        print(self.cmbbox.currentText())
        geocoder = Geocoder(self.iface,"cartociudad", "http://www.cartociudad.es/geocoder/api/geocoder/")
        cmbxText = self.cmbbox.currentText()
        coord = geocoder.find(cmbxText)
        if coord != None:
            self.zoomToPoint(coord[0], coord[1])
               
    def addQbuttonFromLayer(self,layer):
        action = QAction(QIcon(layer.icon), layer.name, self.iface.mainWindow())
        action.setStatusTip(layer.name)
        action.triggered.connect(lambda:layer.addLayerToQgis())
        self.actions.append((self.iface.mainWindow(),action))
        return action        
     
    def convertServicesFromFilesIntoClasses(self,filePath,serviceType):
        file = open(filePath, "r",encoding="utf-8")
        services = []
        
        if serviceType == "wms":               
            lines = file.readlines()
            for line in lines:
                serviceNameAndUrl = line.split(";")
                wms = Wms(self.iface,self.iconPathTopo,serviceNameAndUrl[0],serviceNameAndUrl[1])
                try:
                    layers = wms.getLayersFromUrlService(serviceNameAndUrl[1])
                    for layer in layers:
                        wms.layers.append(layer) 
                        services.append(wms)
                except Exception:
                    print("No ha podido cargarse la capa " +layer.name + " del servicio WMS: "+ serviceNameAndUrl[1] )
                    pass

        else: #serviceType == "wmts":
            lines = file.readlines()
            for line in lines:
                 serviceNameAndUrl = line.split(";")
                 wmts = Wmts(self.iface,self.iconPathTopo,serviceNameAndUrl[0],serviceNameAndUrl[1])
                 try:
                    layers = wmts.getLayersFromUrlService(serviceNameAndUrl[1])
                    for layer in layers:
                        wmts.layers.append(layer)
                        services.append(wmts)
                 except Exception:
                    print("No ha podido cargarse la capa " + layer.name + " del servicio WMTS: "+ serviceNameAndUrl[1] )
                    pass

        file.close()
        
        return services      
        
    def putLayersIntoQmenu(self,service,menu):
        for layer in service.layers:
            layer.setQmenu(menu)
            menu.addAction(self.addQbuttonFromLayer(layer))
                
    def putServicesIntoQmenu(self,services,menu):
        for service in services:
            tmpMenu = self.createQmenu(service.name,service.icon)
            menu.addMenu(tmpMenu)
            self.putLayersIntoQmenu(service, tmpMenu)
                      
    def zoomToRectangule(self, xmin,ymin,xmax, ymax):
        rect = QgsRectangle(xmin, ymin, xmax, ymax) 
        mc = self.iface.mapCanvas()
        mc.setExtent(rect)
        mc.refresh()
        
    def zoomToPoint(self, x, y, scale=None):
        if not scale:
            scale = 0.01 if x < 100 else 1000

        xmin = x-scale/2
        ymin = y-scale/2
        xmax = x+scale/2
        ymax = y+scale/2
        self.zoomToRectangule(xmin, ymin, xmax, ymax)
