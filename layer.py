class Layer:

    def __init__(self,ifaceQgis,iconPath,layerId,layerName,layerUri,menuLayer=None):
        self.iface = ifaceQgis
        self.icon = iconPath
        self.id = layerId
        self.name = layerName
        self.url = layerUri     
        self.menu = menuLayer

        
    def setQmenu(self,qmenu):
        self.menu = qmenu
        
    def setName(self,serviceName):
        self.name = serviceName
        
    def setUrl(self,serviceUrl):
        self.url = serviceUrl 
        
    def addLayerToQgis(self):
        self.iface.addRasterLayer(self.url,self.name,"wms")   
