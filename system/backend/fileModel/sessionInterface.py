from __future__ import annotations
from time import sleep, time
class SessionInterface:
    
    __instance = None
    
    def  __init__(self):
        # {route:{queue:[indecator, ...]}, ...}
        self.__queue = {}
        self.sessionIndex = 0
    
    @classmethod
    def getInstance(cls) -> SessionInterface:
        if not cls.__instance:
            cls.__instance = SessionInterface()
        return cls.__instance
    
    # unique indecator only!
    # timeout in seconds
    @classmethod
    def openSession(cls, route, timeout = None) -> Session | None:
        
        indecator = time() % 1
        
        sessions = cls.getInstance()
        
        
        if route in sessions.__queue:
            while indecator in sessions.__queue[route]['queue']:
                indecator = time() % 1
        
        curSes = Session(indecator)
        # print(sessions.__queue)
        if route in sessions.__queue:
            sessions.__queue[route]['queue'].append(indecator)
        else:
            sessions.__queue[route] = {'queue': [indecator]}
        print(sessions.__queue[route])
        beginning = time()
        while sessions.__queue[route]['queue'].index(indecator): # should be 0 to pass thrue
            now = time()
            if timeout:
                if timeout < now - beginning:
                    curSes.closeSession(route)
                    return None
            sleep(0.1)
            # breakpoint
        return curSes
    
    
class Session:
    
    def __init__(self, id):
        self.id = id
        
    def closeSession(self, route):
        sessions = SessionInterface.getInstance()
        # print(sessions.__dict__)
        if route in sessions._SessionInterface__queue:
            sessions._SessionInterface__queue[route]['queue'].remove(self.id)
            print(sessions._SessionInterface__queue[route])
            return True
        return False
        
            
            
# route first!
def sessionly(f, *args, **kwargs):
    
    def inner(*args, **kwargs):
        try:
            ses = SessionInterface.openSession(args[0])
            # print(args[0])
            # print(ses.id)
        except Exception as e1:
            try:
                ses.closeSession(args[0])
            except Exception as e:
                print(e)
                return
            print(e1)
            return
        res = f(*args, **kwargs)
        
        try:
            ses.closeSession(args[0])
        except Exception as e:
            print('p2', e)
            return
        return res
    
    return inner

        
            