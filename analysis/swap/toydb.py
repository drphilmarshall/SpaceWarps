# ======================================================================

import numpy as np

import datetime

# ======================================================================

class ToyDB(object):
    """
    NAME
        ToyDB

    PURPOSE
        Make a toy database, and serve up data just like Mongo does 
        (except using standard dictionaries).

    COMMENTS

    INITIALISATION
        From scratch.
    
    METHODS AND VARIABLES
        ToyDB.get_classification()
        
    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-18  Started Marshall (Oxford)
    """

# ----------------------------------------------------------------------------

    def __init__(self,pars=None):

        self.client = "Highest bidder"
        self.db = "Hah! This is all fake"

        try: self.surveysize = int(pars['surveysize']) # No. of subjects
        except: self.surveysize = 400
        
        try: self.trainingsize = int(pars['trainingsize']) # No. of subjects
        except: self.surveysize = 400
        
        try: self.population = int(pars['population']) # No. of classifiers
        except: self.population = 100
        
        try: self.enthusiasm = int(pars['enthusiasm']) # Mean no. of classifications per person
        except: self.enthusiasm = 40
        
        try: self.prior = int(pars['lensrate']) # Mean no. of classifications per person
        except: self.prior = 1e-3 # Probability of an image containing a lens

        self.volunteers = self.populate('volunteers')
        trainingset = self.populate('subjects',category='training')
        testset = self.populate('subjects',category='test')
        self.subjects = trainingset + testset
        self.classifications = self.populate('classifications')

        return None

# ----------------------------------------------------------------------------
# Generate various tables in the database:

    def populate(self,things,category=None):

        array = []
        
        if things == 'volunteers':

            for k in range(self.population):
                Name = 'Phil'+str(k)
                
                array.append(Name)
        
        
        elif things == 'subjects':

            if category not in ['training','test']:
                print "ToyDB: confused by category "+category
                sys.exit()
             
            if category == 'training': Nj = self.trainingsize   
            if category == 'test': Nj = self.surveysize   
            
            for j in range(Nj):
                subject = {}
                subject['ID'] = category+'Image'+str(j)

                subject['category'] = category

                if subject['category'] == 'training':
                    if np.random.rand() > 0.5:
                        subject['kind'] = 'sim'
                        subject['truth'] = 'LENS'
                    else:
                        subject['kind'] = 'dud'
                        subject['truth'] = 'NOT'
                        
                elif subject['category'] == 'test':
                    subject['kind'] = 'test'
                    subject['truth'] = 'UNKNOWN'
                    # But we do actually need to know what this is!
                    if np.random.rand() < self.prior: 
                        subject['strewth'] = 'LENS'
                    else:
                        subject['strewth'] = 'NOT'

                array.append(subject)
                
                
        elif things == 'classifications':

            for i in range(self.population*self.enthusiasm):
                classification = {}
                
                classification['Name'] = self.pick_one('volunteers')
                subject = self.pick_one('subjects')
                t = self.pick_one('epochs')
                
                classification['updated_at'] = t
                classification['ID'] = subject['ID']
                classification['category'] = subject['category']
                classification['kind'] = subject['kind']
                classification['truth'] = subject['truth']
                classification['result'] = \
                  self.make_classification(subject=subject,volunteer=classification['Name'])
                
                array.append(classification)


        return array

# ----------------------------------------------------------------------------
# Random selection of something from its list:

    def pick_one(self,things):
    
        if things == 'volunteers':

            k = int(self.population*np.random.rand())
            something = self.volunteers[k]
        
        elif things == 'subjects':

            j = int(len(self.subjects)*np.random.rand())
            something = self.subjects[j]
                
        elif things == 'epochs':

            day = int(14*np.random.rand()) + 1
            hour = int(24*np.random.rand())
            minute = int(60*np.random.rand())
            second = int(60*np.random.rand())
            something = datetime.datetime(2013, 4, day, hour, minute, second, 0)
                
        return something
        
# ----------------------------------------------------------------------------
# Use the hidden confusion matrix of each toy volunteer to classify 
# the subject provided:

    def make_classification(self,subject=None,volunteer=None):
    
        # All toy volunteers are equally skilled! Can ignore them, and
        # just use constant P values.
        PL = 0.9
        PD = 0.8
        
        if subject['category'] == 'training':
            truth = subject['truth']
        elif subject['category'] == 'test':
            truth = subject['strewth']
        
        if truth == 'LENS':
            if np.random.rand() < PL: word = 'LENS'
            else: word = 'NOT'
        
        elif truth == 'NOT':
            if np.random.rand() < PD: word = 'NOT'
            else: word = 'LENS'
                
        return word

# ----------------------------------------------------------------------------
# Return a tuple of the key quantities:

    def digest(self,C):
                
        return str(C['updated_at']),C['Name'],C['ID'],C['category'],C['kind'],C['result'],C['truth']

# ----------------------------------------------------------------------------
# Return a batch of classifications, defined by a time range - either 
# claasifications made 'since' t, or classifications made 'before' t:

    def find(self,word,t):

       batch = []
       
       if word == 'since':
            
            for classification in self.classifications:
                if classification['updated_at'] > t: 
                    batch.append(classification)
       
       elif word == 'before':
            
            for classification in self.classifications:
                if classification['updated_at'] < t: 
                    batch.append(classification)
       
       else:
           print "ToyDB: error, cannot find classifications '"+word+"' "+str(t)

       return batch

# ----------------------------------------------------------------------------
# Return the size of the classification table:

    def size(self):
        
        return len(self.classifications)
        
# ======================================================================

if __name__ == '__main__':

    db = ToyDB()
    
    # Select all classifications that were made before t1.  
    # Note the greater than operator ">".
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
    
