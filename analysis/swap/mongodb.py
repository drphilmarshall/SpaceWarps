# ======================================================================

import numpy as np
import os,sys,subprocess,datetime

try: from pymongo import MongoClient
except:
    print "MongoDB: pymongo is not installed. You can still --practise though"
    sys.exit()
    
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

    def __init__(self):
        
        # Connect to the Mongo:
        try: self.client = MongoClient('localhost', 27017)
        except: 
            print "MongoDB: couldn't connect to the Mongo"
            sys.exit()
        
        try: self.db = self.client['ouroboros_staging']
        except: 
            print "MongoDB: couldn't find a DB called ouroboros_staging"
            sys.exit()

        # Set up tables of subjects, and classifications: 
        self.subjects = self.db['spacewarp_subjects']
        self.classifications = self.db['spacewarp_classifications']
        
        return None

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

if __name__ == '__main__':
    
    # Hard-coded for all Space Warps datasets? Or just beta?
    testGroup = '5154a3783ae74086ab000001'
    trainingGroup = '5154a3783ae74086ab000002'
    
    db = MongoDB()
    
    # Select all classifications that were made before t1.  
    # Note the greater than operator "$lt".
    # Batch is a cursor, it does not read anything into memory yet.
    
    # t1 = datetime.datetime(2013, 4, 4, 23, 59, 59, 0)
    
    # Make sure we catch them all!
    t1 = datetime.datetime(1978, 2, 28, 12,0, 0, 0)
    batch = db.classifications.find({'updated_at': {"$gt": t1}})
    
    # Now, loop over classifications, digesting them.
    
    # Batch has a next() method, which returns the subsequent
    # record, or we can execute a for loop as follows:
    count = 0
    for classification in batch:
                
        # When was this classification made?
        t = classification['updated_at']
        
        # Who made the classification?
        
        # The classification will be identified by either the user_id or
        # the user_ip.  The value will be abstracted into the variable
        # Name.
        
        # Not all records have all keys.  For instance, classifications 
        # from anonymous users will not have a user_id key. We must 
        # check that the key exists, and if so, get the value.
        
        if classification.has_key('user_id'):
            Name = classification['user_id']
        
        else:
            # If there is no user_id, get the ip address...
            # I think we're safe with user_ip.  All records should have 
            # this field. Check the key if you're worried. 
            Name = classification['user_ip']
        
        # Pull out the subject that was classified. Note that by default
        # Zooniverse subjects are stored as lists, because they can 
        # oontain multiple images. 
        
        subjects = classification['subjects']
        
        # Ignore the empty lists (eg the first tutorial subject...)
        if len(subjects) == 0:
            continue
        
        # Get the subject ID:
        for subject in subjects:
            ID = subject['id']
        
        # And finally pull the subject itself from the subject table:
        subject = db.subjects.find_one({'_id': ID})
        
        # Was it a training subject or a test subject?
        if subject.has_key('group_id'):
            groupId = subject['group_id']
        else:
            # Subject is tutorial and has no group id:
            continue
        
        # What kind of subject was it? Training or test? A sim or a dud?
        kind = ''
        if str(groupId) == trainingGroup:
            category = 'training'
            word = subject['metadata']['training']['type']
            if word == 'empty':
                kind = 'dud'
            else:
                kind = 'sim'
        else: # It's a test subject:
            category = 'test'
            kind = 'test'
        
        # What the volunteer say about this subject?
        # First select the annotations:
        annotations = classification['annotations']

        # For sims, we really we want to know if the volunteer hit the 
        # arcs - but this is not yet stored in the database 
        # (issued 2013-04-23). For now, treat sims by just saying that 
        # any number of markers placed constitutes a hit.
        
        # NB: Not every annotation has an associated coordinate 
        # (e.g. x, y) - tutorials fail this criterion.

        N_markers = 0
        for annotation in annotations:
            if annotation.has_key('x'):
                N_markers += 1
        
        if kind == 'sim' or kind == 'test' or kind == 'dud':

            if N_markers == 0:
                result = 'NOT'
            else:
                result = 'LENS'            
        
        # Check we got all 5 items:            
        items = str(t),str(Name),str(ID),kind,result
        if len(items) != 5: print "oops! ",items[:] 
        
        # Count classifications
        count += 1
    
    # Good! Whole database dealt with.
    print "Counted ",count," classifications, that each look like:"
    print items[:]
    
