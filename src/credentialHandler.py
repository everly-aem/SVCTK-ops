# This Python file uses the following encoding: utf-8

import dbHandler as mongo

class credentialHandler:

    def __init__(self, **kwargs)->None:
        '''
        Initialize and take in optional kwargs:
            Username:str
            Password:str
        '''
        pass

    def register(self)->int:
        pass

    def login(self)->int:
        pass

    def isRegistered(self)->bool:
        pass

    def storeSecure(self)->int:
        pass
