# ======================================================================

import swap

import numpy as np

# ======================================================================

class Classifier(object):
    """
    NAME
        Classifier

    PURPOSE
        Model an individual classifier.

    COMMENTS
        The Classifier is a person, whose Name is either a userid or, if
        that is not available, an IP address. The Classifier has a
        History of N classifications, including ND that turned out to be
        duds and NL that turned out to be lenses. (ND+NL) is the total
        number of training subjects classified, and is equal to N in the
        simple "LENS or NOT" analysis. Each Classifier carries a
        "confusion matrix" parameterised by two numbers, PD and PL, the
        meaning of which is as follows:
        
        When a Classifier sees a subject, they say:
        
        | "LENS" when it is "NOT"    "LENS" when it is a "LENS" |
        | with probability (1-PD)    with probability PL        |
        |                                                       |
        | "NOT" when it is "NOT"     "NOT" when it is a "LENS"  |
        | with probability PD        with probability (1-PL)    |
        
        We make the simplest possible assignment for these
        probabilities, namely that PX = 0.5 if NX = 0, and then update
        from there. To make this work, we initialise all Classifiers
        with NL = ND = 2, implying that they got 1 lens right and 1 dud
        right before their classifications were begun. Obviously this is
        a horrible hack. 
        
        
    INITIALISATION
        name
    
    METHODS
        Classifier.updateExpertise()     Calculate the expected 
                                         information per classification
        
    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-17  Started Marshall (Oxford)
    """

# ----------------------------------------------------------------------

    def __init__(self,name):
        self.name = name
        self.ND = 2.0
        self.NL = 2.0
        self.PD = 0.5
        self.PL = 0.5
        self.expertise = self.update_expertise()
        self.history = np.array([self.expertise])
        return None

# ----------------------------------------------------------------------

    def __str__(self):
        return 'individual classifier named %s with expertise %.2f' % \
               (self.name,self.expertise)       
        
# ----------------------------------------------------------------------
# Compute expected information per classification:

    def update_expertise(self):
        plogp = np.zeros([2,2])
        plogp[0,0] = self.PD*np.log2(self.PD)
        plogp[0,1] = (1-self.PD)*np.log2(1-self.PD)
        plogp[1,0] = (1-self.PL)*np.log2(1-self.PL)
        plogp[1,1] = self.PL*np.log2(self.PL)
        self.expertise = 0.5*(np.sum(plogp) + 2)
        return self.expertise
        
# ----------------------------------------------------------------------
# Update confusion matrix with latest result:
#   crowd.member[Name].reportedly(saidItWas='LENS',actuallyItWas='NOT')

    def said(self,it_was=None,actually_it_was=None):
        if it_was==None or actually_it_was==None:
            pass
        else:
            if actually_it_was=='LENS':
                self.PL = (self.PL*self.NL + (it_was==actually_it_was))/(1+self.NL)
                self.NL += 1
            elif actually_it_was=='NOT':
                self.PD = (self.PD*self.ND + (it_was==actually_it_was))/(1+self.ND)
                self.ND += 1
            else:
                raise Exception("Apparently, the subject was actually a "+str(actually_it_was))
            self.history = np.append(self.history,self.update_expertise())
        return

# ----------------------------------------------------------------------
# Plot classifier's history, as an overlay on an existing plot:

    def plot_history(self):
        return

# ======================================================================
   
