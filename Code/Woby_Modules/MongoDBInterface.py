"""
MongoDBInterface.py
Object to handle MongoDB client connection and CRUD tasks.

author: @justjoshtings
created: 3/27/2022
"""
from pymongo import MongoClient
import bson
from Woby_Modules.Logger import MyLogger
from datetime import datetime

class MongoDBInterface:
    '''
    Object to handle MongoDB client connection and CRUD tasks.
    '''
    def __init__(self, host, port, database, collection, log_file=None):
        '''
        Params:
            self: instance of object
            host (str): host name of MongoDB db
            port (str): port to access MongoDB db
            database (str): database name to use
            collection (str): collection name to use
            log_file (str): default is None to not have logging, otherwise, specify logging path ../filepath/log.log
        '''
        self.host = host
        self.port = port
        self.client = MongoClient(host, port)
        self.database = self.client[database]
        self.collection = self.database[collection]

        self.LOG_FILENAME = log_file
        if self.LOG_FILENAME:
            # Set up a specific logger with our desired output level
            self.mylogger = MyLogger(self.LOG_FILENAME)
            # global MY_LOGGER
            self.MY_LOGGER = self.mylogger.get_mylogger()
            self.MY_LOGGER.info(f"{datetime.now()} -- [MONGODB STARTING] Connecting to DB on HOST:{self.host}, PORT:{self.port}, DB:{self.database}, COLLECTION:{self.collection}...")
    
    def insert_documents(self, documents):
        '''
        Method to insert documents into specified collection

        Params:
            self: instance of object
            documents (list of dict or dict) : Payload document to insert into collection
                                        documents = [{ "name": "Amy", "address": "Apple st 652"}, { "name": "Hannah", "address": "Mountain 21"}]
                                        OR
                                        documents = { "name": "Michael", "address": "Valley 345"}
        '''
        if self.LOG_FILENAME:
            self.MY_LOGGER.info(f"{datetime.now()} -- [MONGODB INSERT] Inserting payload to DB:{self.database}, COLLECTION:{self.collection}...")

        if isinstance(documents, list):
            cursor = self.collection.insert_many(documents)
        elif isinstance(documents, dict):
            cursor = self.collection.insert_one(documents)

        if self.LOG_FILENAME:
            self.MY_LOGGER.info(f"{datetime.now()} -- [MONGODB INSERT] Insertion complete...")

    def get_documents(self, query={}, projection={}, sort=[], limit=1, size=False, show=False):
        '''
        Method to retrieve documents from specified collection

        Params:
            self: instance of object
            query (dict): default None if no query, {'aws_account_id': aws_account.account_number}
            projection (dict): default None if no projection, {'aws_account_id': 1}
            sort (list of tuple): default None if not sorting, sort=[( '_id', pymongo.DESCENDING )]
            limit (int): default == 1 to find_one(), else find().limit(limit)
            size (Boolean): default = False to not show bson MB size, True to show instead of returning documents, max is 16MB
            show (Boolean): default False to not print out retrieved documents, True to print
        
        Returns:
            documents (list of dict): list of dict where each dict is a separate document
        '''
        documents = list()

        returned_documents = self.collection.find(query, projection=projection, sort=sort).limit(limit)

        for document in returned_documents:
            
            if show:
                print(document)
                if size:
                    print('Bytes: ', self.get_document_size(document))
        
            documents.append(document)
        
        return documents

    def delete_documents(self, query, delete_many=False, delete_all=False):
        '''
        Method to delete documents from specified collection

        Params:
            self: instance of object
            query (dict): represent what fields and criteria to filter on, query = { "address": {"$regex": "^S"} }
            delete_many (Boolean): default False to not delete many records in batch, True to delete many at once
            delete_all (Boolean): default False to not delete all records from collection, True to delete all
        '''
        if self.LOG_FILENAME:
            self.MY_LOGGER.info(f"{datetime.now()} -- [MONGODB DELETE] Deleting query {query} from DB:{self.database}, COLLECTION:{self.collection}...")

        if delete_all:
            query = {}
            cursor = self.collection.delete_many(query)
        else:
            if delete_many:
                if dict:
                    raise AssertionError(f"query is empty dict. query cannot be {query} for delete_many == True, set delete_all == True and delete_many == False to delete all")
                cursor = self.collection.delete_many(query)
            else:
                cursor = self.collection.delete_one(query)

        if self.LOG_FILENAME:
            self.MY_LOGGER.info(f"{datetime.now()} -- [MONGODB DELETE] Completed deletion...")

    def get_document_size(self, doc):
        '''
        Method to get bson document size, max is 16MB
        
        Params:
            self: instance of object
            doc (bson document): document to get size of
        '''
        return len(bson.BSON.encode(doc))

    def find_duplciates(self, pipeline):
        '''
        Method find duplicates based on a pipeline
        
        Params:
            self: instance of object
            pipeline (list of dictionary): desribe pipeline to query and aggregate data on, 
                                           pipeline = [
                                               {"$group":{"_id":"$full_name", "count":{"$sum":1}}}, 
                                               {"$match": {"_id" :{ "$ne" : 'null' } , "count" : {"$gt": 1} } },
                                               {"$project": {"full_name" : "$_id", "_id" : 0} }
                                               ]
        '''
        print('Number of ducplicates: ', len(list(self.collection.aggregate(pipeline))))

        return list(self.collection.aggregate(pipeline))
    
    




if __name__ == "__main__":
    print("Executing MongoDBInterface.py")
else:
    print("Importing MongoDBInterface")