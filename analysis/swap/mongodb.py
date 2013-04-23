# ======================================================================

import numpy as np
import os,sys,subprocess,datetime
from pymongo import MongoClient

# ======================================================================

class MongoDB(object):
    """
    NAME
        MongoDB

    PURPOSE
        Interrogate an actual mongo database, and serve up data for a 
        a simple python analysis.

    COMMENTS
        The mongodb server must be running in the background (perhaps 
        started from another shell. A typical sequence would be:
        
        cd workspace
        mongorestore spacewarps-2013-04-06_20-07-28
        mongod --dbpath . &
        
        pymongo can be obtained by pip install.
        This sequence is carried out by the MongoDB class itself, via a 
        system call.
        
        Basic operation is to define a "classification" tuple, that 
        contains all the information needed by a probabilistic online 
        analysis. At present, in SWAP, this is a simple "LENS" or "NOT"
        classification, with classification agent confusion matrices 
        updated using the training subjects, and the test subjects'
        Pr(LENS|d) updated using these matrices.


    INITIALISATION
        
    
    METHODS AND VARIABLES
        ToyDB.get_classification()
        
    BUGS

    AUTHOR
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-18  Started Marshall (Oxford)
    """

# ----------------------------------------------------------------------------

    def __init__(self,dumpname=None):

        # self.dumpname = dumpname
        #        
        # # Keep a record of what goes on:
        # self.logfilename = os.getcwd()+'/'+self.dumpname+'.log'
        # self.logfile = open(self.logfilename,"w")
        # 
        # # Start the Mongo server in the background:
        # subprocess.call(["mongorestore",self.dumpname],stdout=self.logfile,stderr=self.logfile)
        # os.chdir(self.dumpname)
        # self.cleanup()
        # self.process = subprocess.Popen(["mongod","--dbpath","."],stdout=self.logfile,stderr=self.logfile)
        # 
        # # Check everything is working:
        # if self.process.poll() == None: print "MongoDB: server is up and running"
        
        # Connect to the Mongo:
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['ouroboros_staging']

        self.subjects = self.db['spacewarp_subjects']
        self.classifications = self.db['spacewarp_classifications']

        # for subject in self.subjects.find():
        #   print subject

        # for classification in self.classifications.find():
        #   print classification['annotations']
        
        return

# ----------------------------------------------------------------------------
# # Return a tuple of the key quantities:
# 
#     def get_classification(self,i):
#         
#         C = self.classifications[i]    
#         
#         return C['Name'],C['ID'],C['category'],C['result'],C['kind']
# 
# ----------------------------------------------------------------------------
# Return the size of the classification table:

    def size(self):
        
        return len(self.classifications)
        
# ----------------------------------------------------------------------------

    def terminate(self):
    
        self.process.terminate()
        self.logfile.close()
        self.cleanup()

        return

# ----------------------------------------------------------------------------

    def cleanup(self):
    
        try: os.remove('mongod.lock')
        except: pass
        try: os.remove('local.0')
        except: pass
        try: os.remove('local.ns')
        except: pass
        try: os.removedirs('journal')
        except: pass
        try: os.removedirs('_tmp')
        except: pass
        
        return

# ======================================================================
# None of this code works. It's just to show Amit what I want to do!

if __name__ == '__main__':
    
    testGroup = '5154a3783ae74086ab000001'
    trainingGroup = '5154a3783ae74086ab000002'
    
    m = MongoDB('ouroboros_staging')

    # Get a batch of classifications between t1 and t2:
    
    t1 = datetime.datetime(2013, 4, 4, 20, 33, 45, 0)
    t2 = datetime.datetime(2013, 4, 5, 20, 33, 45, 0)
    # batch = m.classifications.find({'updated_at': {"$gt": t1}, 'updated_at:': {"$lt": t2}})
    
    # Select classifications that came after t1.  Note the greater than operator "$gt".
    # Batch is a cursor, it does not read anything into memory yet.
    batch = m.classifications.find({'updated_at': {"$gt": t1}})
    
    # Here is where items are read.  Batch has a next() method, which returns the subsequent
    # record.  Or we can execute a for loop.
    for classification in batch:
        
        # Who made the classification?
        
        # The classification will be identified by either the user_id or
        # the user_ip.  The value will be abstracted into the variable user.
        
        # Not all records have all keys.  For instance, classifications from
        # anonymous users will not have a user_id key. We must check that the key exists,
        # and if so, get the value.
        if classification.has_key('user_id'):
          user = classification['user_id']
        # If there is no user_id, get the ip address...
        else:
          # I think we're safe with user_ip.  All records should have this field.
          # Check the key if you're worried. 
          user = classification['user_ip']
        
        # Pull out the subject that was classified:
        subjects = classification['subjects']
        if len(subjects) == 0:
          continue
        
        for subject in subjects:
          ID = subject['id']
        
        subject = m.subjects.find_one({'_id': ID})
        
        # Was it a training subject or a test subject?
        if subject.has_key('group_id'):
          groupId = subject['group_id']
        else:
          # Subject is tutorial and has no group id
          continue
        
        kind = ''
        if str(groupId) == trainingGroup:
            # Was it a sim or a dud?
            word = subject['metadata']['training']['type']
            
            if word == 'empty':
              kind = 'dud'
            else:
              kind = 'sim'
        
        if kind == 'sim':
          
          # Faking: Any number of markers constitutes a hit.
          
          # Select the annotations
          annotations = classification['annotations']
          
          # Start an annotation counter
          nAnnotations = 0
          
          # Loop over annotations. NOTE: Not every annotation has an associated coordinate (e.g. x, y)
          for annotation in annotations:
            if annotation.has_key('x'):
              nAnnotations += 1
          
          result = 'LENS'
          if nAnnotations == 0:
            result = 'NOT'
          
        
        
        continue
        
        # # What was the result of the classification?
        # if category == 'training':
        #     if kind == 'sim':
        #         # Did the user hit the arcs?
        #         success = classification['hit_arcs'] # True or False?
        #         if success: result = 'LENS'
        #         else: result = 'NOT'
        #     else:
        #         # Did the user make no annotations?
        #         success = classification['skipped'] # True or False?
        #         if success: result = 'NOT'
        #         else: result = 'LENS'
        # 
        # else: 
        #     foundsomething = (len(annotations) > 0) # True or False?
        #     if foundsomething: result = 'LENS'
        #     else: result = 'NOT'
        # 
        # print Name,ID,category,result,kind
        
    
    m.terminate()
