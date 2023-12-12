# This Python file uses the following encoding: utf-8

from pymongo import MongoClient as mc
import os, json
import src.credentialHandler as credientialHandler

class mongoHandler:
    def __init__(self, logger):
        self.logger = logger
        # Get cfg information and setup vars for use
        _absDIR = os.getcwd()
        logger.info('Opening cfg file')
        with open(os.path.join(_absDIR, '_internal', 'FTSTK_config.json'), 'r') as jsonFile:
                    self.cfg = json.loads(jsonFile.read())

        self.cfg = self.cfg['DB']
        self.logger.debug(f'Config read as: {self.cfg}')

        match self.cfg['db_access']:
            case 0:
                userLevelName = 'FTStech'
            case 1:
                userLevelName = 'FTSmanager'
            case 2:
                userLevelName = 'FTSadmin'
            case _:
                raise Exception

        self.logger.debug(f'Level Name used: {userLevelName}')
        self.logger.info('Getting credential handler')
        credHandler = credientialHandler.internalCredHandler()

        try:
            self.logger.info('Getting password for userLevelName')
            userLevelPassword = credHandler.getPass(userLevelName)
        except:
            self.logger.error('Unable to get password from system!')
            raise Exception

        try:
            self.client = mc(
                host='mongodb+srv://aemftscluster0.1kekelk.mongodb.net',
                username=userLevelName,
                password=userLevelPassword
            )

            self.logger.debug(f'Mongo Cluster Information: {self.client.server_info()}')
        except:
            return

        self.logger.debug(self.cfg['db_db_name'])
        self.logger.debug(self.cfg['db_collection_names'])

        # Get all collections from cfg and load into mem
        self.collectionNames = []
        for collection in self.cfg['db_collection_names']:
            self.collectionNames.append(collection)


    def getDB(self, collection:str):
        self.logger.info('Getting DB...')
        try:
            db = self.client[self.cfg['db_db_name']] # Return the db
            self.logger.debug('DB grabbed!')
            return db[collection]
        except Exception as e:
            # Error grabbing the db from connection, does the DB exist?
            self.logger.exception(e)
            self.logger.error('Unable to access the DB!')
            #return e

    def pushCollection(self, data):
        self.logger.info('Pushing data to collection...')
        err_list = []

        # When a user is ready to push data to the db this method will handle both single and multiple items
        # Runs after connection to the required db is made
        for item in data:
            # each item in a sn, add each of these dicts into the db, need to det. what db from sub key pair in sn
            try:
                collection = self.getDB(collection=item['destCollection'])
                collection.insert_one(item)
            except Exception as e:
                err_list.append(e)

        if len(err_list) == 0:
            return 0
        else:
            self.logger.error(err_list)
            return err_list


    def getCollection(self, searchWord:str):
        self.logger.info('Looking for collection to use...')
        # Grab data from a search and return it to the user
        # Searching through a SN only db and then when we know which db the data is stored in, connect and retrive it
        # Returns search Word and db that contains the item, calls getDB()
        results = []
        for collection in self.collectionNames:
            self.logger.debug(f'Collection Name being searched: {collection}')
            try:
                dbAccesser = self.getDB(collection)
            except Exception as e:
                return e
            search = dbAccesser.find({'Serial_Number':searchWord})
            self.logger.debug(f'Raw search: {search}')
            for entry in search:
                results.append(entry)
                print(entry)
            if len(results) != 0: break
        self.logger.debug(f'Results: {results}')
        return results
