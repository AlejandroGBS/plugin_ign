import sys
import importlib.util
import subprocess
import pkg_resources



class Utils:
    
    def __init__(self,iface):
        self.iface = iface
        
    def installLib(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])        
            
            
    def checkLib(self, libName, minimumVer):
        pythonVer = sys.version_info

        if pythonVer[0]  >= 3:
            if pythonVer[1] >= 3:
                if libName in sys.modules:
                    self.checkLibversion(libName, minimumVer)
                    print(f"{libName!r} already in sys.modules")
                elif (importlib.util.find_spec(libName)) is not None:
                    spec = importlib.util.find_spec(libName)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[libName] = module
                    spec.loader.exec_module(module)
                    print(f"{libName!r} has been imported")
                else:
                    #self.installLib(libName)  
                    print('libreria instalada')              
            elif pythonVer[1] < 3:
                try:
                     import libName
                except ImportError as e:
                   # self.installLib(libName)
                    print('libreria no instalada')
                    self.installLibVersion(libName, minimumVer)   
            elif pythonVer[0] == 2:   
                print("you must update your Python version")
    
    def getLibVersion(self, libName):
        ver = pkg_resources.get_distribution(libName).version
        return ver 
    
    def isHigherVersion(self,installed, minimum):
        installedMay = installed.split('.')[0]
        installedMin = installed.split('.')[1]
        installedRev = installed.split('.')[2] 
        minimumMay = minimum.split('.')[0]
        minimumMin = minimum.split('.')[1]
        minimumRev = minimum.split('.')[2] 
        
        if installedMay >= minimumMay:
            if installedMin >= minimumMin:
                if installedRev >= minimumRev:
                    return True
        return False
    
    def checkLibversion(self, libName, minVer):
        installedVer = self.getLibVersion(libName)
        if not self.isHigherVersion(installedVer, minVer):
            self.installLibVersion(libName, minVer)
        else:
             print(f"{libName!r} has the minimum version required")
            
    def installLibVersion(self, name, version):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", name + "==" + version])                
        except ImportError as e:
            print("unable to install the required lib version :" + name + "==" + version + ", try to do it manually.")
                