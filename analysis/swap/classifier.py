# ======================================================================

import swap

import numpy as np
import pylab as plt

# ======================================================================

class Classifier(object):
    """
    NAME
        Classifier

    PURPOSE
        Provide an agent who will interpret the classifications of an 
        individual volunteer.

    COMMENTS
        A Classifier is an agent who is assigned to represent a 
        volunteer, whose Name is either a Zooniverse userid or, if
        that is not available, an IP address. A Classifier has a
        History of N classifications, including ND that turned out to be
        duds and NL that turned out to be lenses. (ND+NL) is the total
        number of training subjects classified, and is equal to N in the
        simple "LENS or NOT" analysis. Each Classifier carries a
        "confusion matrix" parameterised by two numbers, PD and PL, the
        meaning of which is as follows:
        
        A Classifier assumes that its volunteer says:
        
        | "LENS" when it is NOT    "LENS" when it is a LENS  |
        | with probability (1-PD)    with probability PL     |
        |                                                    |
        | "NOT" when it is NOT     "NOT" when it is a LENS   |
        | with probability PD        with probability (1-PL) |
        
        It makes the simplest possible assignment for these
        probabilities, namely that PX = 0.5 if NX = 0, and then updates
        from there using the training subjects such that 
        PX = NX_correct / NX at all times. For example, if the 
        volunteer is right about 80% of the simulated lenses they see, 
        the agent will assign PL = Pr("LENS"|LENS) = 0.8.
        
        To make the numbers come out right, we initialise all 
        Classifiers with NL = ND = 2 as well as PL = PD = 0.5, implying
        that they got 1 lens right and 1 dud right before their 
        classifications were begun. This is conservative (in 
        that it probably underestimates the volunteers' natural 
        lens-spotting talent, and also a horrible hack. 
        
        The big assumption the Classifier is making is that its 
        volunteer has a single, constant PL and a single, constant 
        PD, which it estimates using all the volunteer's data. This is
        clearly sub-optimal, but might be good enough for a first 
        attempt. We'll see!
        
        
    INITIALISATION
        name
    
    METHODS
        Classifier.update_contribution()  Calculate the expected 
                                          information contributed 
                                          per classification
        Classifier.said(it_was=X,actually_it_was=Y)     Read report.
        Classifier.plot_history(axes)
        
    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-17:  Started Marshall (Oxford)
    """

# ----------------------------------------------------------------------

    def __init__(self,name,pars):
        self.name = name
        self.PD = pars['initialPD']
        self.PL = pars['initialPL']
        self.ND = 1.0/self.PD
        self.NL = 1.0/self.PL
        self.N = 0
        self.contribution = self.update_contribution()
        self.traininghistory = {'ID':'tutorial','I':np.array([self.contribution]),'PL':np.array([self.PL]),'PD':np.array([self.PD])}
        self.testhistory = {'ID':[],'I':np.array([])}
        return None

# ----------------------------------------------------------------------

    def __str__(self):
        return 'individual classifier named %s with contribution %.2f' % \
               (self.name,self.contribution)       
        
# ----------------------------------------------------------------------
# Compute expected information per classification:

    def update_contribution(self):
        plogp = np.zeros([2,2])
        plogp[0,0] = self.PD*np.log2(self.PD)
        plogp[0,1] = (1-self.PD)*np.log2(1-self.PD)
        plogp[1,0] = (1-self.PL)*np.log2(1-self.PL)
        plogp[1,1] = self.PL*np.log2(self.PL)
        self.contribution = 0.5*(np.sum(plogp) + 2)
        return self.contribution
        
# ----------------------------------------------------------------------
# Update confusion matrix with latest result:
#   eg.  collaboration.member[Name].heard(it_was='LENS',actually_it_was='NOT')

    def heard(self,it_was=None,actually_it_was=None,ignore=False):

        if it_was==None or actually_it_was==None:
            pass

        else:
            if not ignore:
                if actually_it_was=='LENS':
                    self.PL = (self.PL*self.NL + (it_was==actually_it_was))/(1+self.NL)
                    self.PL = np.min([self.PL,swap.PLmax])
                    self.NL += 1

                elif actually_it_was=='NOT':
                    self.PD = (self.PD*self.ND + (it_was==actually_it_was))/(1+self.ND)
                    self.PD = np.min([self.PD,swap.PDmax])
                    self.ND += 1
                else:
                    raise Exception("Apparently, the subject was actually a "+str(actually_it_was))
 
            # Always log progress, even if not learning:
            self.traininghistory['I'] = np.append(self.traininghistory['I'],self.update_contribution())
            self.traininghistory['PL'] = np.append(self.traininghistory['PL'],self.PL)
            self.traininghistory['PD'] = np.append(self.traininghistory['PD'],self.PD)

        return

# ----------------------------------------------------------------------
# Plot classifier's history, as an overlay on an existing plot:

    def plot_history(self,axes):
    
        plt.sca(axes)
        I = self.traininghistory['I']
        N = np.linspace(1, len(I), len(I), endpoint=True)
        
        # Information contributions:
        plt.plot(N, I, color="green", alpha=0.1, linewidth=2.0, linestyle="-")
        plt.scatter(N[-1], I[-1], color="green", alpha=0.5)
        
        return

# ======================================================================
   
