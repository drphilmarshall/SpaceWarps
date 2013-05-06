# ======================================================================

import numpy as np
import os,sys,datetime

try: from pymongo import MongoClient
except:
    print "MongoDB: pymongo is not installed. You can still --practise though"
    sys.exit()

# Hard-coded for all Space Warps datasets? Or just beta?
testGroup = '5154a3783ae74086ab000001'
trainingGroup = '5154a3783ae74086ab000002'
    
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
        - groupIds are hard-coded, and so could go wrong any time.
        - arc hits in sim subjects are not yet recorded.
        
    AUTHOR
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-18  Started: Marshall (Oxford)
      2013-04-23  Correct Mongo calls supplied: Kapadia (Adler) 
    """

# ----------------------------------------------------------------------------

    def __init__(self):
        
        # Connect to the Mongo:
        try: self.client = MongoClient('localhost', 27017)
        except: 
            print "MongoDB: couldn't connect to the Mongo"
            print "MongoDB: try doing something like this in a different shell:"
            print "  mongorestore spacewarps-2013-04-06_20-07-28"
            print "  mongod --dbpath . &"
            sys.exit()
        
        try: self.db = self.client['ouroboros_staging']
        except: 
            print "MongoDB: couldn't find a DB called ouroboros_staging"
            print "MongoDB: did your mongorestore work correctly?"
            sys.exit()

        # Set up tables of subjects, and classifications: 
        self.subjects = self.db['spacewarp_subjects']
        self.classifications = self.db['spacewarp_classifications']
        
        return None

# ----------------------------------------------------------------------------
# Return a batch of classifications, defined by a time range - either 
# claasifications made 'since' t, or classifications made 'before' t:

    def find(self,word,t):

       if word == 'since':
            batch = self.classifications.find({'updated_at': {"$gt": t}})
       
       elif word == 'before':
            batch = self.classifications.find({'updated_at': {"$lt": t}})
       
       else:
           print "MongoDB: error, cannot find classifications '"+word+"' "+str(t)

       return batch

# ----------------------------------------------------------------------------
# Return a tuple of the key quantities, given a cursor pointing to a 
# record in the classifications table:

    def digest(self,classification):
        
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
            return None
        
        # Get the subject ID:
        for subject in subjects:
            ID = subject['id']
        
        # And finally pull the subject itself from the subject table:
        subject = self.subjects.find_one({'_id': ID})
        
        # Was it a training subject or a test subject?
        if subject.has_key('group_id'):
            groupId = subject['group_id']
        else:
            # Subject is tutorial and has no group id:
            return None
        
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
        
        # And finally, what's the truth about this subject?
        if kind == 'sim':
            truth = 'LENS'
        elif kind == 'dud':
            truth = 'NOT'
        else:    
            truth = 'UNKNOWN'
        
        # Check we got all 7 items:            
        items = str(t),str(Name),str(ID),category,kind,result,truth
        if len(items) != 7: print "MongoDB: digest failed: ",items[:] 
                         
        return items[:]


# ----------------------------------------------------------------------------
# Return the size of the classification table:

    def size(self):
        # BUG: I don't actually know how to return the length of the 
        # classification table...
        return 1e6
        
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
    
    db = MongoDB()
    
    # Select all classifications that were made before t1.  
    # Note the greater than operator "$gt".
    # Batch is a cursor, it does not read anything into memory yet.
    # Make sure we catch them all!
    t1 = datetime.datetime(1978, 2, 28, 12,0, 0, 0)

    batch = db.find('since',t1)

    # Now, loop over classifications, digesting them.
    
    # Batch has a next() method, which returns the subsequent
    # record, or we can execute a for loop as follows:
    count = 0
    for classification in batch:
        
        items = db.digest(classification)
        
        # Check we got all 7 items:            
        if items is not None:
            if len(items) != 7: 
                print "oops! ",items[:]
            else:    
                # Count classifications
                count += 1
    
    # Good! Whole database dealt with.
    print "Counted ",count," classifications, that each look like:"
    print items[:]
    
