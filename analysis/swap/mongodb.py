# ======================================================================

import numpy as np
import os,sys,datetime

try: from pymongo import MongoClient
except:
    print "MongoDB: pymongo is not installed. You can still --practise though"
    # sys.exit()

# Hard-coded for all Space Warps datasets:
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
        
        This sequence is carried out by the MongoDB class itself, via a 
        system call. pymongo can be obtained by pip install.
        
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
            print "  mongod --dbpath . &"
            print "  mongorestore spacewarps-2013-04-06_20-07-28"
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
            batch = self.classifications.find({'updated_at': {"$gt": t}},timeout=False)
       
       elif word == 'before':
            batch = self.classifications.find({'updated_at': {"$lt": t}},timeout=False)
       
       else:
           print "MongoDB: error, cannot find classifications '"+word+"' "+str(t)

       return batch

# ----------------------------------------------------------------------------
# Return a tuple of the key quantities, given a cursor pointing to a 
# record in the classifications table:

    def digest(self,classification,survey,method=False):
        
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
        
        # Get the subject ID, and also its Zooniverse ID:
        for subject in subjects:
            ID = subject['id']
            ZooID = subject['zooniverse_id']
        
        # Pull out the annotations and get the stage the classification was made at:
        annotations = classification['annotations']
        
        stage = 1
        for annotation in annotations:
            if annotation.has_key('stage'):
                stage = annotation['stage']
        
        # Also get the survey name!
        project = "CFHTLS"
        for annotation in annotations:
            if annotation.has_key('project'):
                project = annotation['project']
        
        # Check project: ignore this classification by returning None 
        # if classification is from a different project:
        if project != survey:
            # print "Fail! A classification from "+project+" ( != "+survey+" ), stage = ",stage
            return None
        # else:
            # Success! A classification from "+project+" ( = "+survey+" ), stage = ",stage
        
        # Now pull the subject itself from the subject table:
        subject = self.subjects.find_one({'_id': ID},timeout=False)
        
        # Was it a training subject or a test subject?
        if subject.has_key('group_id'):
            groupId = subject['group_id']
        else:
            # Subject is tutorial and has no group id:
            return None
        
        metadata = subject['metadata']        
        
        # Check stage:
        if metadata.has_key('stage2'):
            if stage == 1: 
                # This happens when the data is uploaded, but the site has
                # not been taken down... Need to ignore these classifications!
                # print "WARNING: classification labelled stage 1, while subject is stage 2!"
                return None
       
        
        # What kind of subject was it? Training or test? A sim or a dud?
        kind = ''
        if str(groupId) == trainingGroup:
            category = 'training'
            things = metadata['training']
            # things is either a list of dictionaries, or in beta, a 
            # single dictionary:
            if type(things) == list:
                thing = things[0]
            else:
                thing = things
            word = thing['type']
            if (word == 'lensing cluster' \
               or word == 'lensed galaxy' \
               or word == 'lensed quasar'):
                kind = 'sim'
            else:
                kind = 'dud'
        else: # It's a test subject:
            category = 'test'
            kind = 'test'
        
        # What's the URL of this image?
        if subject.has_key('location'):
            things = subject['location']
            location = things['standard']
        else:
            location = None
        
        
        # What did the volunteer say about this subject?

        # For sims, we really we want to know if the volunteer hit the 
        # arcs - but this is not yet stored in the database 
        # (issued 2013-04-23). For now, treat sims by just saying that 
        # any number of markers placed constitutes a hit.
        
        # NB: Not every annotation has an associated coordinate 
        # (e.g. x, y) - tutorials fail this criterion.

        N_markers = 0
        simFound = False
        for annotation in annotations:
            if annotation.has_key('x'): 
                N_markers += 1
        
        # Detect whether sim was found or not:
        if kind == 'sim':
            if method:
                # Use the marker positions!
                for annotation in annotations:
                    if annotation.has_key('simFound'):
                        string = annotation['simFound']
                        if string == 'true': simFound = True
            else:
                if N_markers > 0: simFound = True
        
        # Now turn indicators into results:
        if kind == 'sim':
            if simFound:
                result = 'LENS'
            else:
                result = 'NOT'
              
        elif kind == 'test' or kind == 'dud':
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
          
        # Testing to see what people do:
        # print "In db.digest: kind,N_markers,simFound,result,truth = ",kind,N_markers,simFound,result,truth
        
        # Check we got all 10 items:            
        items = t.strftime('%Y-%m-%d_%H:%M:%S'),str(Name),str(ID),str(ZooID),category,kind,result,truth,str(location),str(stage)
        if len(items) != 10: print "MongoDB: digest failed: ",items[:] 
                         
        return items[:]


# ----------------------------------------------------------------------------
# Return the size of the classification table:

    def size(self):
        # BUG: I don't actually know how to return the length of the 
        # classification table...
        return 1e5
        
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

    batch = db.find('since',t1,timeout=False)

    # How many did we get?
    total = db.classifications.count()
    print "Whoah! Found ",total," classifications!"
    print "Here's the last one:"
    for classification in db.classifications.find(timeout=False).skip(total-1).limit(1):
        items = db.digest(classification)
        print items[:]
    
    print "Reading them all one by one, just for fun:"
    
    # Now, loop over classifications, digesting them.
    
    # Batch has a next() method, which returns the subsequent
    # record, or we can execute a for loop as follows:
    count = 0
    for classification in batch:
        
        items = db.digest(classification)
        
        if count == total: print classification
        
        # Check we got all 9 items:            
        if items is not None:
            if len(items) != 9: 
                print "oops! ",items[:]
            else:    
                # Count classifications
                count += 1
                
        if np.mod(count,int(total/80.0)) == 0: 
            sys.stdout.write('.')
            sys.stdout.flush()
           
                   
    # Good! Whole database dealt with.
    print "Counted ",count," classifications, that each look like:"
    print items[:]
    
