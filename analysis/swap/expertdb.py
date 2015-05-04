# ======================================================================

import numpy as np
import os,sys,datetime


# Hard-coded for all Space Warps datasets:
testGroup = '5154a3783ae74086ab000001'
trainingGroup = '5154a3783ae74086ab000002'

# ======================================================================

class ExpertDB(object):
    """
    NAME
        ExpertDB

    PURPOSE
        Interrogate an actual expert database (csv file), and serve up data for
        a simple python analysis.

    COMMENTS
        Basic operation is to define a "classification" tuple, that
        contains all the information needed by a probabilistic online
        analysis. At present, in SWAP, this is a simple "LENS" or "NOT"
        classification, with classification agent confusion matrices
        updated using the training subjects, and the test subjects'
        Pr(LENS|d) updated using these matrices.

        Expert databases are assumed to include the following columns:
            SubjectID  : what was classified
            AgentID  : who classified
            Classification  : the classification
            (This is currently case sensitive. That might change and probably should.)
        They may also include these:
            updated_at




    INITIALISATION


    METHODS AND VARIABLES
        ToyDB.get_classification()

    AUTHOR
      This file is part of the Space Warps project, and is distributed
      under the MIT license by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-18  Started: Marshall (Oxford)
      2013-04-23  Correct Mongo calls supplied: Kapadia (Adler)
      2015-04-30  Made Expert version using MongoDB as base class
    """

# ----------------------------------------------------------------------------

    def __init__(self,csv_path):

        self.classifications = np.recfromcsv(csv_path, case_sensitive=True)
        # TODO: Check that the classifications has all the things we want
        columns = ['SubjectID', 'AgentID', 'Classification']
        for column in columns:
            if column not in self.classifications.dtype.names:
                raise Exception('expertDB: Missing critical column {0}'.format(column))

        return None

# ----------------------------------------------------------------------------
# Return a batch of classifications, defined by a time range - either
# claasifications made 'since' t, or classifications made 'before' t:

    def find(self,word,t):

        # TODO: let's just return all the classifications for now

        return self.classifications

# ----------------------------------------------------------------------------
# Return a tuple of the key quantities, given a cursor pointing to a
# record in the classifications table:

    def digest(self,classification,survey,method=False):
        """
        items = db.digest(classification,survey,method=use_marker_positions)
tstring,Name,ID,ZooID,category,kind,flavor,X,Y,location,classification_stage,at_x,at_y = items

items = t.strftime('%Y-%m-%d_%H:%M:%S'),str(Name),str(ID),str(ZooID),category,kind,flavor,result,truth,str(location),str(classification_stage),str(annotation_x),str(annotation_y)
        """

        # When was the classification made? TODO: Assume it's just some time.
        t = datetime.datetime(2100, 1, 1, 12, 0, 0, 0)

        # Who made the classification?
        Name = classification['AgentID']

        # Get the subject ID
        ID = classification['SubjectID']
        # Make up a ZooID by assuming it's the same as the ID
        ZooID = ID

        # TODO: For now just put in a filler annotation
        classification_stage = 0

        # What kind of subject? TODO: Assume for now that it is unknown.
        category = 'test'
        kind = 'test'
        flavor = 'test'
        location = None

        # What did the volunteer -- I mean, expert -- say about this subject?
        # TODO: Two annotations at (-1, -1)
        annotation_x = [-1, -1]
        annotation_y = [-1, -1]

        # Now turn indicators into results. This is where we convert expert
        # grades.
        grade = classification['Classification']
        if grade > 0:
            result = 'LENS'
        else:
            result = 'NOT'

        # And finally, what's the truth about this subject? TODO: Assume
        # UNKNOWN
        truth = 'UNKNOWN'

        items = t.strftime('%Y-%m-%d_%H:%M:%S'),str(Name),str(ID),str(ZooID),category,kind,flavor,result,truth,str(location),str(classification_stage),str(annotation_x),str(annotation_y)
        if len(items) != 13: print "MongoDB: digest failed: ",items[:] 

        return items[:]

# ----------------------------------------------------------------------------
# Return the size of the classification table:

    def size(self):
        raise NotImplementedError

# ======================================================================

if __name__ == '__main__':
    
    db = ExpertDB(csv_path=sys.argv[1])

    # Select all classifications that were made before t1.
    # Note the greater than operator "$gt".
    # Batch is a cursor, it does not read anything into memory yet.
    # Make sure we catch them all!
    t1 = datetime.datetime(1978, 2, 28, 12,0, 0, 0)

    batch = db.find('since',t1)

    # How many did we get?
    total = db.classifications.size
    print "Whoah! Found ",total," classifications!"
    print "Here's the last one:"
    for classification in db.classifications:
        items = db.digest(classification, 'experts')
        print items[:]

    print "Reading them all one by one, just for fun:"

    # Now, loop over classifications, digesting them.

    # Batch has a next() method, which returns the subsequent
    # record, or we can execute a for loop as follows:
    count = 0
    for classification in batch:

        items = db.digest(classification, 'experts')

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

