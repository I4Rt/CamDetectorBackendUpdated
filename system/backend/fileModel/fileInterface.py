from __future__ import annotations
from os import getcwd, listdir, mkdir, remove, rmdir, path
from time import time
import cv2

from fileModel.sessionInterface import SessionInterface, sessionly
from numpy import ndarray
from time import sleep
import json
class FileMethods:
    
    baseRoute = path.join(getcwd().replace('\\', '/'), 'system/backend/fileSystem')

    @classmethod
    def _readTextFile(cls, route:str) -> str:
        # fileInterface = cls.getInstance()
        realPath = path.join(cls.baseRoute, route).replace('\\', '/')
        # print(cls.baseRoute, realPath)
        # identy = time()
        # SessionInterface.openSession(realPath, identy)
        # sleep(0.5) #testing
        try:
            with open(realPath, 'r') as file:
                data = file.read()
                # SessionInterface.closeSession(realPath, identy)
                return data
        except Exception as e:
            # SessionInterface.closeSession(realPath, identy)
            raise( Exception(f'{route}: FileReadException: {type(e)}'))
        
    @classmethod
    def _writeTextFile(cls, route:str, data:str, mode:['w', 'a']='w') -> None:
        # fileInterface = cls.getInstance()
        realPath = path.join(cls.baseRoute, route).replace('\\', '/')
        # identy = time()
        # SessionInterface.openSession(realPath, identy)
        # sleep(0.5) #testing
        try:
            with open(realPath, mode) as file:
                file.write(data)
                # SessionInterface.closeSession(realPath, identy)
                return data
        except Exception as e:
            # SessionInterface.closeSession(realPath, identy)
            raise( Exception(f'{route}: FileWriteException: {type(e)}'))
    
    @classmethod
    def _deleteFile(cls, route:str) -> bool:
        # fileInterface = cls.getInstance()
        realPath = path.join(cls.baseRoute, route).replace('\\', '/')
        # identy = time()
        # SessionInterface.openSession(realPath, identy)
        try:
            # sleep(0.5) #testing
            if not path.isdir(realPath):
                remove(realPath)
                return True
            return False
        except Exception as e:
            # SessionInterface.closeSession(realPath, identy)
            raise( Exception(f'{route}: FileDeleteException: {type(e)}'))
        
    @classmethod
    def _delFolder(cls, route) -> True:
        # fileInterface = cls.getInstance()
        realPath = path.join(cls.baseRoute, route).replace('\\', '/')
        # identy = time()
        # SessionInterface.openSession(realPath, identy)
        if path.isdir(realPath):
            for localRoute in listdir(realPath):
                if path.isdir(localRoute):
                    cls._delFolder(localRoute)
                else:
                    cls._deleteFile(localRoute)
        # SessionInterface.closeSession(realPath, identy)
        return True
    
    @classmethod
    def _createFolder(cls, route, folderName):
        try:
            realPath = path.join(cls.baseRoute, route).replace('\\', '/')
            print('join', realPath)
        except Exception as e:
            print('path join exception', e)
        if path.exists(realPath):
            newPath = path.join(realPath, folderName).replace('\\', '/')
            try:
                print('creating', newPath)
                mkdir(newPath)
            except Exception as e:
                print('inside e', e)
            print('inside created')
            return True
        return False
    
    @classmethod
    def _writeImage(cls, route:str, cv2Image) -> None:
        # fileInterface = cls.getInstance()
        #realPath = path.join(cls.baseRoute, route).replace('\\', '/')
        # SessionInterface.openSession(realPath, identy)
        route = 'system/backend/fileSystem/' + route
        try:
            print('saving image', route)
            return cv2.imwrite(route.replace('/', '\\'), cv2Image)
            # SessionInterface.closeSession(realPath, identy)
        except Exception as e:
            print(f'ImageSaveException: {type(e)}')
            # SessionInterface.closeSession(realPath, identy)
            raise( Exception(f'{route}: ImageSaveException: {type(e)}'))
    
    @classmethod
    def _readImage(cls, route:str) -> ndarray:
        # fileInterface = cls.getInstance()
        realPath = path.join(cls.baseRoute, route).replace('\\', '/')
        # SessionInterface.openSession(realPath, identy)
        # sleep(0.5) #testing
        try:
            img = cv2.imread(realPath)
            # SessionInterface.closeSession(realPath, identy)
            return img
        except Exception as e:
            # SessionInterface.closeSession(realPath, identy)
            raise( Exception(f'{route}: ImageReadException: {type(e)}'))
      
class FileSystemInterface(FileMethods):
    
    def __init__(self):
        FileMethods.__init__(self)
        
    @classmethod
    def doFileSystemJsonFileWorks(cls, route, foo):
        @sessionly
        def inner(r):
            data = cls._readTextFile(r)
            data = foo(data)
            return FileMethods._writeTextFile(r, data)
        return inner(route)
    
    @classmethod 
    def createFile(cls, route):
        @sessionly
        def inner(r):
            FileMethods._writeTextFile(r, '')
        inner(route)
        
    @classmethod
    def readFileSystemTxt(cls, route):
        @sessionly
        def inner(r):
            data = FileMethods._readTextFile(r)
            # print('read data is', data)
            return data
        return inner(route)

    @classmethod
    def getImage(cls, route:str):
        @sessionly
        def inner(r):
            return FileMethods._readImage(r)
        return inner(route)
    
    @classmethod
    def saveImage(cls, route:str, cv2Image):
        
        @sessionly
        def inner(r, img):
            return FileMethods._writeImage(r, img)
        return inner(route, cv2Image)
        
    @classmethod
    def createFolder(cls, route, folderName):
        @sessionly
        def inner(r, fN):
            return cls._createFolder(r, fN)
        return inner(route, folderName)
        
    @classmethod
    def delete(cls, route):
        @sessionly
        def innerForFile(r):
            return FileMethods._deleteFile(r)
        
        @sessionly
        def innerForFolder(r):
            return FileMethods._delFolder(r)
        
        res =  innerForFile(route) # true if del is sucsess and route fas file like
        if not res:
            res = innerForFolder(route)
        return res
    
    @classmethod
    def checkExist(cls, route):
        @sessionly
        def inner(r):
            fullRoute = path.join(cls.baseRoute, r).replace('\\', '/')
            return path.exists(fullRoute)
        return inner(route)
    
    @classmethod
    def getFolderFiles(cls, route):
        @sessionly
        def inner(r):
            fullRoute = path.join(cls.baseRoute, r)
            return listdir(fullRoute)
        return inner(route)
    
    
    '''
    @classmethod
    def getFolderFiles(cls, route):
        @sessionly
        def inner(r):
            fullRoute = path.join(cls.baseRoute, r)
            lst = listdir(fullRoute)
            res = {}
            for fileName in lst:
                curDir = path.join(fullRoute, fileName)
                if path.isdir(curDir):
                    res[fileName] = inner()
        return inner(route)
    '''
    
if __name__ == "__main__":
    from threading import Thread
    fileRoute = r'C:\Users\Марков Владимир\Documents\GitHub\CamDetectorBackendUpdated\system\fileSystem\test\testDataFile.txt'
    imgRoute = r'C:\Users\Марков Владимир\Documents\GitHub\CamDetectorBackendUpdated\system\fileSystem\test\megan-fox.jpg'
    
    
    ##### TODO
    # @sessionly
    # def task1(fileRoute):
    #     # FileInterface._readImage(imgRoute)
    #     filedata = FileMethods.readTextFile(fileRoute)
    #     filedata = json.loads(filedata)
    #     if not ('counter' in list(filedata.keys())):
    #         filedata['counter'] = 0
    #     filedata['counter'] += 1
    #     FileMethods.writeTextFile(fileRoute, json.dumps(filedata))
    #     print('counter', filedata['counter'])
    #     sleep(2)

    # task1(fileRoute)
    
    # t1 = Thread(target=task1)
    # t2 = Thread(target=task1)
    # t3 = Thread(target=task1)
    
    # t1.start()
    # t2.start()
    # t3.start()
    
    def appendCouter(data):
        data = json.loads(data)
        try:
            data['counter'] += 1
        except:
            data['counter'] = 1
        print('set data from', data['counter'] - 1, 'to', data['counter'])
        return json.dumps(data)
    
    # FileSystemInterface.doFileSystemJsonFileWorks(fileRoute, appendCouter)
    
    t1 = Thread(target=FileSystemInterface.doFileSystemJsonFileWorks, args=(fileRoute, appendCouter))
    t2 = Thread(target=FileSystemInterface.readFileSystemTxt, args=[(fileRoute)])
    t3 = Thread(target=FileSystemInterface.readFileSystemTxt, args=[(fileRoute)])
    t4 = Thread(target=FileSystemInterface.doFileSystemJsonFileWorks, args=(fileRoute, appendCouter))
    t5 = Thread(target=FileSystemInterface.doFileSystemJsonFileWorks, args=(fileRoute, appendCouter))
    
    t1.start()
    t2.start()
    t4.start()
    t3.start()
    t5.start()