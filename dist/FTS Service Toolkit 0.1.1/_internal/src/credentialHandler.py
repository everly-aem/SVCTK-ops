# This Python file uses the following encoding: utf-8

from passlib.context import CryptContext
import keyring
#import keyring.util.platform as keyringPlatform

# Takes the follwing fields and stores them securly inside the loacl OS password vault (windows: credential vault, macOS: keychain)
# Entry -> 'username' or key for the password/crediential being saved
# Password -> the raw plain password to be compaired with SCRAM on mongoDB

class internalCredHandler:

    def __init__(self)->None:
        keyring.get_keyring()

        self._namespace = 'FTS_Toolkit'

        return None

    def getPass(self, entry:str)->str:
        # get the password to loginto mongoDB with
        password = keyring.get_password(self._namespace, entry)
        if None == password: raise Exception
        return password

    def storeSecure(self, entry:str, password:str)->int:
        keyring.set_password(self._namespace, entry, password)
        return 0
