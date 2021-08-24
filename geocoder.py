# ################################
# ######## Imports #################
# ################################

from urllib.parse import unquote, urlencode
import requests
import json
from pyproj import Proj, transform
import re
from enum import Enum
from moduloborrar import  moduloborrar_dialog
from .moduloborrar_dialog import borrarDialog


class Geocoder:
    
    def __init__(self,ifaceQgis,serviceName,serviceUrl):
        self.iface = ifaceQgis
        self.name = serviceName
        self.url = serviceUrl
        self.query = ''
        
    
    def find(self,query):
        x, y, epsg = self.isCoordinates(query)
        if not (x != None and y != None and epsg != None) :
            addresses = self.getCandidatesInJson(query) #"calle iglesia 5, madrid")
            ventana = borrarDialog(parent=self.iface.mainWindow())
            response = ventana.doModal(addresses)
            tcr =ventana.tableWidget.currentRow()
            if response != 0:
                if tcr >= 0:
                    epsg = self.iface.mapCanvas().mapSettings().destinationCrs().authid()
                    coord = self.getCoordinatesFromCandidate(addresses[tcr], epsg)
        else:
            coord = self.transformCoordinates(x,y,"EPSG:4326",epsg)
        return coord           
          
    
    def getCandidatesInJson(self,query):
        try:
            ploads= {'limit':5, 'q': query}
            url = self.url + "candidatesJsonp"
            rq = requests.get(url,params=ploads)
            data = rq.text.split("(", 1)[1].strip(")")
            return json.loads(data)
        except:
           tb = traceback.format_exc()
           raise Exception("Error:Getting candidates, Query" + query) + tb
         
    def getAddress(self,id, type, portal):
        try:        
            ploads = {'id': id, 'type':type, 'portal':portal}
            url = self.url + "findJsonp"
            rq = requests.get(url, params=ploads)
            data = rq.text.split("(", 1)[1].strip(")")
            return json.loads(data)
        except:
           tb = traceback.format_exc()
           raise Exception("Error:Getting address, ID: " + id) + tb
    
    def getCoordinatesFromCandidate(self,jsonCandidate, epsg=None):
        try:
            addrss  =  self.getAddress(jsonCandidate["id"], jsonCandidate["type"], jsonCandidate["portalNumber"])
            coord = [addrss["lng"],addrss["lat"]]
            if epsg != None and epsg != "EPSG:4326":       
                coord = self.transformCoordinates(addrss["lng"],addrss["lat"],"EPSG:4326",epsg)
            return coord
        except:
            tb = traceback.format_exc()
            raise Exception("Error:Getting coordinates, ID: " + jsonCandidate["id"]) + tb
    
    def transformCoordinates(self, x, y,epsgOri, epsgDest):
        try:
            inProj = Proj(epsgOri)
            outProj = Proj(epsgDest)
            x2,y2 = transform(inProj,outProj,x,y)
            return [x2,y2]
        except:
            tb = traceback.format_exc()
            raise Exception("Error:Transforming coordinates, EPSG" +epsgDest + "x,y"  +x +y) + tb
        
        
    def getQueryTypeData(self,query):
        x, y, epsg = self.isCoordinates(query)
        if x:
            x2, y2 = self.transformCoordinates(x, y, epsg, "EPSG:4326")
        
      
    
    def isCoordinates(self,query):
        expression = r"^\s*(EPSG:\d+\s+)?([+-]?[0-9]*[.,]?[0-9]+)\s*([+-]?[0-9]*[.,]?[0-9]+)\s+(EPSG:\d+)?\s*$" 
        result = re.search(expression, query, re.IGNORECASE)
        if result:
            epsg1, x, y, epsg2 = result.groups()
            epsg = epsg1 if epsg1 else epsg2 if epsg2 else None
            x = float(x.replace(',', '.'))
            y = float(y.replace(',', '.'))
        else:
            x, y, epsg = None, None, None

        return x, y, epsg
   
   

class geocoderQueryType(Enum):
    ADDRESS = 1
    COORDINATES = 2
    
    
    