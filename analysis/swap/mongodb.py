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

        self.dumpname = dumpname
       
        # Keep a record of what goes on:
        self.logfilename = os.getcwd()+'/'+self.dumpname+'.log'
        self.logfile = open(self.logfilename,"w")
        
        # Start the Mongo server in the background:
        subprocess.call(["mongorestore",self.dumpname],stdout=self.logfile,stderr=self.logfile)
        os.chdir(self.dumpname)
        self.cleanup()
        self.process = subprocess.Popen(["mongod","--dbpath","."],stdout=self.logfile,stderr=self.logfile)
        
        # Check everything is working:
        if self.process.poll() == None: print "MongoDB: server is up and running"
        
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

    m = MongoDB('spacewarps-2013-04-06_20-07-28')

    # Get a batch of classifications between t1 and t2:
    
    t1 = datetime.datetime(2013, 4, 4, 20, 33, 45, 0)
    t2 = datetime.datetime(2013, 4, 5, 20, 33, 45, 0)
    batch = m.classifications.find(updated_at > t1 and updated_at < t2)
        
    for classification in batch:
        
        # Who made the classification?
        Name = classification['user_id']
        # If there is no user_id, get the ip address...
        
        # Pull out the subject that was classified:
        ID = classification['subject_id']
        subject = m.subjects.find_one(subject_id == ID)
        
        # Was it a training subject or a test subject?
        category = subject['category']
        
        if category == 'training':
            # Was it a sim or a dud?
            kind = subject['kind']
        
        # What was the result of the classification?
        if category == 'training':
            if kind == 'sim':
                # Did the user hit the arcs?
                success = classification['hit_arcs'] # True or False?
                if success: result = 'LENS'
                else: result = 'NOT'
            else:
                # Did the user make no annotations?
                success = classification['skipped'] # True or False?
                if success: result = 'NOT'
                else: result = 'LENS'
        
        else: 
            foundsomething = (len(annotations) > 0) # True or False?
            if foundsomething: result = 'LENS'
            else: result = 'NOT'
        
        print Name,ID,category,result,kind
        
    
    m.terminate()
