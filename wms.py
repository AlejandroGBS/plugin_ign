# ################################
# ######## Imports #################
# ################################

from urllib.parse import unquote, urlencode
from sys import exit
from owslib.util import *
from qgis.core import QgsRasterLayer,QgsProject
from .layer import Layer


try:
    from owslib.util import *
except:
    print("Depencencies - owslib util is not present")
    
try:
    from owslib.wms import WebMapService
    import owslib

    print("Depencencies - owslib version: {}".format(owslib.__version__))
except ImportError as e:
    print("Depencencies - owslib wms is not present")

try:
    from owslib.util import HTTPError

    print("Depencencies - HTTPError within owslib")
except ImportError as e:
    print(
        "Depencencies - HTTPError not within owslib."
        " Trying to get it from urllib2 directly."
    )
    from urllib3.exceptions import HTTPError


class Wms:
    
    def __init__(self,ifaceQgis,iconPath,serviceName,serviceUrl,menuWms=None):
        self.iface = ifaceQgis
        self.icon = iconPath
        self.menu = menuWms
        self.name = serviceName
        self.url = serviceUrl 
        self.layers =[]
        
    def setQmenu(self,qmenu):
        self.menu = qmenu

    def setName(self,serviceName):
        self.name = serviceName
        
    def setUrl(self,serviceUrl):
        self.url = serviceUrl 
     
    def addLayer(self,layer):
        layers.append(layer)   
    
    def addRasterLayer(self,wmsNameAndUrl):
        self.iface.addRasterLayer(wmsNameAndUrl[1],wmsNameAndUrl[0],"wms")
        
    def getLayersFromUrlService(self,serviceUrl): 
        
        layers = []  
        
        current_crs = str(self.iface.mapCanvas().mapSettings().destinationCrs().authid())

        qgis_wms_formats = (
            "image/png",
            "image/png8",
            "image/jpeg",
            "image/svg",
            "image/gif",
            "image/geotiff",
            "image/tiff",
        )

# opening WMTS
        wms_url_getcap = serviceUrl + "?request=GetCapabilities"

        try:
            authe = Authentication(verify=False)
            wms = WebMapService(wms_url_getcap,version="1.3.0",auth=authe)
        except TypeError as e:
            print("OWSLib mixing str and unicode args", str(e))
            wms = WebMapService(unicode(wms_url_getcap))
        except ServiceException as e:
            print("WMTS - Bad operation: " + wms_url_getcap, str(e))
        except HTTPError as e:
            print("WMTS - Service not reached: " + wms_url_getcap, str(e))
        except Exception as e:
            print(str(e))
            raise

        print(dir(wms))


# Get a layer
        print("Available layers: ", list(wms.contents))
        
        for layer_name in  list(wms.contents):            
                        
            wms_lyr = wms[layer_name]
            layer_title = wms_lyr.title
            layer_id = wms_lyr.id
            print("First layer picked: ", layer_title, layer_name, layer_id)   
            
# GetTile URL
            wms_lyr_url = wms.getOperationByName("GetMap").methods
            wms_lyr_url = wms_lyr_url[0].get("url")
            if wms_lyr_url[-1] == "&":
                wms_lyr_url = wms_lyr_url[:-1]
            else:
                pass

            wmts_url_params = {
                "SERVICE": "WMS",
                "VERSION": "1.0.0",
                "REQUEST": "GetCapabilities",
                "layers": layer_id,
                "format": "image/png",
                "styles": "",
                "url": wms_lyr_url,
            }
            wmts_url_final = unquote(urlencode(wmts_url_params))      
           
            layer = Layer(self.iface,self.icon,layer_id,layer_title,wmts_url_final)
            
            layers.append(layer)
        
        return layers
