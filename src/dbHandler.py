# This Python file uses the following encoding: utf-8

from pymongo import MongoClient as mc
import os, json

class mongoHandler:
    def __init__(self):
        # Get cfg information and setup vars for use
        _absDIR = os.getcwd()
        with open(os.path.join(_absDIR, 'FTSTK_config.json'), 'r') as jsonFile:
                    self.cfg = json.loads(jsonFile.read())

        self.connectionString:str = self.cfg["DB"]["connStr"]

        # Get all dbs from cfg and load into mem
        self.collectionNames = []
        for collection in self.cfg["DB"]["collectionNames"]:
            self.collectionNames.append(collection)


    def getDB(self, collection:str):
        # Grab DB that is needed, connection is made only when user requires it
        try:
            client = mc(self.connectionString)
        except Exception as e:
            # Error on connection, bad connection str? Bad user?
            return e

        try:
            db = client[self.cfg["DB"]["dbName"]] # Return the db
            return db[collection]
        except Exception as e:
            # Error grabbing the db from connection, does the DB exist?
            return e

    def pushCollection(self, data):
        err_list = []

        # When a user is ready to push data to the db this method will handle both single and multiple items
        # Runs after connection to the required db is made
        for item in data:
            # each item in a sn, add each of these dicts into the db, need to det. what db from sub key pair in sn
            try:
                collection = self.getDB(collection=item["destCollection"])
                collection.insert_one(item)
            except Exception as e:
                err_list.append(e)

        if len(err_list) == 0:
            return 0
        else:
            return err_list


    def getCollection(self, searchWord:str):
        # Grab data from a search and return it to the user
        # Searching through a SN only db and then when we know which db the data is stored in, connect and retrive it
        # Returns search Word and db that contains the item, calls getDB()
        results = []
        for collection in self.collectionNames:
            print(collection)
            dbAccesser = self.getDB(collection)
            search = dbAccesser.find({"Serial_Number":searchWord})
            for entry in search:
                results.append(entry)
                print(entry)
            if len(results) != 0: break
        print(results)
        return results

    def closeDB(self, db):
        # After work is complete, close the connection and inform the user of operation status
        pass
