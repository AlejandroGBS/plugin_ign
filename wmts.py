# ################################
# ######## Imports #################
# ################################

from urllib.parse import unquote, urlencode
from sys import exit
from owslib.util import *
from qgis.core import QgsRasterLayer,QgsProject
from .layer import Layer

try:
    from owslib.wmts import WebMapTileService
    import owslib

    print("Depencencies - owslib version: {}".format(owslib.__version__))
except ImportError as e:
    print("Depencencies - owslib is not present")

try:
    from owslib.util import HTTPError

    print("Depencencies - HTTPError within owslib")
except ImportError as e:
    print(
        "Depencencies - HTTPError not within owslib."
        " Trying to get it from urllib2 directly."
    )
    from urllib3.exceptions import HTTPError

# ################################
# ######## Variables  ###############
# ################################

class Wmts:
    
    def __init__(self,ifaceQgis,iconPath,serviceName,serviceUrl,menuWmts=None):
        self.iface = ifaceQgis
        self.icon = iconPath
        self.menu = menuWmts
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
            
    def addRasterLayer(self, wmsNameAndUrl):
        self.iface.addRasterLayer(wmsNameAndUrl[1], wmsNameAndUrl[0], "wms")
             
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
        wmts_url_getcap = serviceUrl + "?request=GetCapabilities"

        try:
            authe = Authentication(verify=False)
            wmts = WebMapTileService(wmts_url_getcap,auth=authe)
        except TypeError as e:
            print("OWSLib mixing str and unicode args", str(e))
            wmts = WebMapTileService(unicode(wmts_url_getcap))
        except ServiceException as e:
            print("WMTS - Bad operation: " + wmts_url_getcap, str(e))
        except HTTPError as e:
            print("WMTS - Service not reached: " + wmts_url_getcap, str(e))
        except Exception as e:
            print(str(e))
            raise

        print(dir(wmts))


# Get a layer
        print("Available layers: ", list(wmts.contents))
        
        for layer_name in  list(wmts.contents):

            wmts_lyr = wmts[layer_name]
            layer_title = wmts_lyr.title
            layer_id = wmts_lyr.id
            print("First layer picked: ", layer_title, layer_name, layer_id)
    

# Tile Matrix Set & SRS
            print(
                "Available tile matrix sets: ",
                wmts_lyr.tilematrixsets,
                type(wmts_lyr.tilematrixsets),
            )
            def_tile_matrix_set = wmts_lyr.tilematrixsets[0]
            print(dir(def_tile_matrix_set))
    
            if current_crs in wmts_lyr.tilematrixsets:
                print("It's a SRS match! With map canvas: " + current_crs)
                tile_matrix_set = wmts.tilematrixsets.get(current_crs).identifier
                srs = current_crs
            elif "EPSG:4326" in wmts_lyr.tilematrixsets:
                print("It's a SRS match! With standard WGS 84 (EPSG:4326)")
                tile_matrix_set = wmts.tilematrixsets.get("EPSG:4326").identifier
                srs = "EPSG:4326"
            elif "EPSG:900913" in wmts_lyr.tilematrixsets:
                print("It's a SRS match! With Google (EPSG:900913)")
                tile_matrix_set = wmts.tilematrixsets.get("EPSG:900913").identifier
                srs = "EPSG:900913"
            else:
                print("Searched SRS not available within service CRS.")
                tile_matrix_set = wmts.tilematrixsets.get(def_tile_matrix_set).identifier
                srs = tile_matrix_set
    
# Format definition
            wmts_lyr_formats = wmts.getOperationByName("GetTile").formatOptions
            formats_image = [f.split(" ", 1)[0] for f in wmts_lyr_formats if f in qgis_wms_formats]
            if len(formats_image):
                if "image/png" in formats_image:
                    layer_format = "image/png"
                elif "image/jpeg" in formats_image:
                    layer_format = "image/jpeg"
                else:
                    layer_format = formats_image[0]
            else:
        # try with PNG
                layer_format = "image/png"
    
# Style definition
            print("Available styles: ", wmts_lyr.styles)
    

# Themes listing
# print("Available themes: ", wmts.themes)
# lyr_themes = wmts.themes.keys()[0]


# GetTile URL
            wmts_lyr_url = wmts.getOperationByName("GetTile").methods
            wmts_lyr_url = wmts_lyr_url[0].get("url")
            if wmts_lyr_url[-1] == "&":
                wmts_lyr_url = wmts_lyr_url[:-1]
            else:
                pass
        
# URL construction
            wmts_url_params = {
                "SERVICE": "WMTS",
                "VERSION": "1.0.0",
                "REQUEST": "GetCapabilities",
                "layers": layer_id,
                "crs": srs,
                "format": layer_format,
                "styles": "",
                "tileMatrixSet": tile_matrix_set,
                "url": wmts_lyr_url,
            }
            wmts_url_final = unquote(urlencode(wmts_url_params))
            print(wmts_url_final)
            
            layer = Layer(self.iface,self.icon,layer_id,layer_title,wmts_url_final)
            
            layers.append(layer)
        
        return layers
            #self.iface.addRasterLayer(wmts_url_final, "Auto - " + layer_title, "wms")
    
#             qgis_wmts_lyr_manual = QgsRasterLayer(wmts_url_final, "Auto - " + layer_title, "wms")
#             if qgis_wmts_lyr_manual.isValid():
#                 QgsProject.instance().addMapLayer(qgis_wmts_lyr_manual)
#             else:
#                 print(qgis_wmts_lyr_manual.error().message())
    
#         manual_lyr = "contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/jpeg&layers=usa:states&styles=&tileMatrixSet=EPSG:4326&url=http://suite.opengeo.org/geoserver/gwc/service/wmts?request%3DGetCapabilities"
#         qgis_wmts_lyr = QgsRasterLayer(manual_lyr, "Manual - " + layer_title, "wms")
#         if qgis_wmts_lyr.isValid():
#             QgsProject.instance().addMapLayer(qgis_wmts_lyr)
#             pass
#         else:
#             print(qgis_wmts_lyr.error().message())
    
    # to remove manual layer
    # QgsProject.instance().removeMapLayer(qgis_wmts_lyr_manual)