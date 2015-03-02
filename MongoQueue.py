import random
import pymongo
from datetime import datetime, timedelta
import traceback
from pymongo import Connection

DEFAULT_INSERT = {
    "locked_by": None,
    "locked_at": None
}

registeredNames={}
compare="low"

'''
 Queue is called wih a dbname and collection
 Names of jobs have to be registered with a function
 Configure is used to synchronize different workers and filter based on priorities
 Once queue is started it cant be stopped. Keeps polling for data from the database.


'''
class Queue(object):


    def __init__(self, dbname, collectionName):
        conn=pymongo.MongoClient()
        db=conn[dbname]
        self.collection = db[collectionName]



    def put(self,name,data,nextRunAt,frequency,priority):
        ''' function to add into the database'''
        job = dict(DEFAULT_INSERT)
        self.priority=priority
        job['nextRunAt'] = datetime.strptime(nextRunAt, '%b %d %Y %I:%M%p')
        job['name'] = name
        job["data"]=data
        job["priority"]=priority
        job["frequency"]=frequency
        return self.collection.insert(job)


    def register(self,name_of,handler):
        ''' Registers name of the job with a function to be called once retrieved from the database'''
        registeredNames[name_of]=handler
        #frequencies[self.name_of]=int(frequency)
        return 0


    def resetJob(self,job):
        #updates a job to be run next based on frequency. 
        job = self._wrap_one(self.collection.find_and_modify(
            query={"_id":job.id},
            update={"$set": {
                "nextRunAt":datetime.now()+timedelta(hours=int(job.frequency))}},
            sort=[('_id', pymongo.ASCENDING)],
            new=1,
            limit=1,
            ))

    def configure(self,consumer_id="Worker"+str(random.random()),prio=None):
        #Assigns a name to a worker as well as filters based on priority
        job = dict(DEFAULT_INSERT)
        self.consumer_id=consumer_id
        self.priority=prio
        return self.priority

    def executeSomething(self):
        # Call the db call to get an Job item or None if there are no jobs.
        # Check every X ms to see if there is any new job.
        #while xxx : Thread.sleep
        #Checks to see if priority is assigned. If it is filters based on priority
        #A job is searched for which is older than current time and is registered with a function
        #Once job is found, reset is called based on frequency

        if self.priority != None:
            job = self._wrap_one(self.collection.find_and_modify(
                query={"locked_by": None,
                       "locked_at": None,
                       "name":{"$in":registeredNames.keys()},
                       "priority":self.priority,
                       "nextRunAt": {"$lt": datetime.now()}},
                update={"$set": {
                    "nextRunAt":datetime.now(),
                    "locked_by": self.consumer_id,
                    "locked_at": datetime.now()}},
                sort=[('_id', pymongo.ASCENDING)],
                new=1,
                limit=1,
                ))
        else:
            job = self._wrap_one(self.collection.find_and_modify(
                query={"locked_by": None,
                       "locked_at": None,
                       "name":{"$in":registeredNames.keys()},
                       "nextRunAt": {"$lt": datetime.now()}},
                update={"$set": {
                    "nextRunAt":datetime.now(),
                    "locked_by": self.consumer_id,
                    "locked_at": datetime.now()}},
                sort=[('_id', pymongo.ASCENDING)],
                new=1,
                limit=1,
                ))

        if job:
            return registeredNames[job.name](job.data),self.resetJob(job)

    def start(self):
        #polls for any changes in a collection
        while True:
            self.executeSomething()

    def _wrap_one(self, data):
        return data and Job(self, data) or None

#To handle properties of jobs

class Job(object):

    def __init__(self, queue, job):
        self._queue = queue
        self._raw = job
        self._data = job["data"]
        self._name = job["name"]


    @property
    def frequency(self):
        return self._raw["frequency"]
        #return sel

    @property
    def raw(self):
        return self._raw

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._raw["_id"]



