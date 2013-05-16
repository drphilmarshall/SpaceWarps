# ======================================================================

import swap

import numpy as np
import pylab as plt

# Every subject starts with the following probability of being a LENS:
prior = 2e-4

# ======================================================================

class Subject(object):
    """
    NAME
        Subject

    PURPOSE
        Model an individual Space Warps subject.

    COMMENTS
        Each subject knows whether it is a test or training subject, and
        it knows its truth (which is different according to category).
        Each subject (regardless of category) has a probability of 
        being a LENS, and this is tracked along a trajectory.
        
        Subject state:
          * active    Still being classified
          * inactive  No longer being classified
        Training subjects are always active. Retired = inactive.

        Subject status: 
          * detected  P > detection_threshold
          * rejected  P < rejection_threshold
          * undecided otherwise
        
        Subject categories:
          * test      A subject from the test (random, survey) set
          * training  A training subject, either a sim or a dud
        
        Subject kinds:
          * test      A subject from the test (random, survey) set
          * sim       A training subject containing a simulated lens
          * dud       A training subject known not to contain any lenses
        
        Subject truths:
          * LENS      It actually is a LENS (sim)
          * NOT       It actually is NOT a LENS (dud)
          * UNKNOWN   It could be either (test)

        
    INITIALISATION
        ID
    
    METHODS
        Subject.described(by=X,as=Y)     Calculate Pr(LENS|d) given 
                                         classifier X's assessment Y
        Subject.plot_trajectory(axes)
        
    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    trajectory
      2013-04-17  Started Marshall (Oxford)
    """

# ----------------------------------------------------------------------

    def __init__(self,ID,ZooID,category,kind,truth,thresholds,location):

        self.ID = ID
        self.ZooID = ZooID
        self.category = category
        self.kind = kind
        self.truth = truth

        self.state = 'active'
        self.status = 'undecided'
            
        self.probability = prior
        self.trajectory = np.array([self.probability])
        self.exposure = 0
        
        self.detection_threshold = thresholds['detection']
        self.rejection_threshold = thresholds['rejection']
        
        self.location = location
                
        return None

# ----------------------------------------------------------------------

    def __str__(self):
        return 'individual (%s) subject, ID %s, Pr(LENS|d) = %.2f' % \
               (self.kind,self.ID,self.probability)       
        
# ----------------------------------------------------------------------
# Update probability of LENS, given latest classification:
#   eg.  sample.member[ID].was_described(by=agent,as_being='LENS',at_time=t)

    def was_described(self,by=None,as_being=None,at_time=None,ignore=0):

        # Update agent: 
        by.N += 1

        if by==None or as_being==None:
            pass

        # Skip straight past inactive subjects.
        # It would be nice to warn the user that inactive subjects
        # should not be being classified:  this can happen if the
        # subject has not been cleanly retired  in the Zooniverse
        # database. However, this leads to a huge  stream of warnings,
        # so best not do that... Note also that training subjects 
        # cannot go inactive - but we need to ignore classifications of
        # them after they cross threshold, for the training set to 
        # be useful in giving us the selection function. What you see in 
        # the trajectory plot is the *status* of the training subjects,
        # not their *state*.
        
        elif self.state == 'inactive' \
          or self.status == 'detected' or self.status == 'rejected':
            
            # print "SWAP: WARNING: subject "+self.ID+" is inactive, but appears to have been just classified"
            pass

        # Deal with active subjects. Ignore the classifier until they 
        # have seen NT > a_few_at_the_start (ie they've had a 
        # certain amount of training):
        else:
            
            if by.NT > ignore:
               
                if as_being == 'LENS':
                    likelihood = by.PL
                    likelihood /= (by.PL*self.probability + (1-by.PD)*(1-self.probability))

                elif as_being == 'NOT':
                    likelihood = (1-by.PL)
                    likelihood /= ((1-by.PL)*self.probability + by.PD*(1-self.probability))

                else:
                    raise Exception("Unrecognised classification result: "+as_being)

                # Update subject:
                self.probability = likelihood*self.probability
                if self.probability < swap.pmin: self.probability = swap.pmin

                self.trajectory = np.append(self.trajectory,self.probability)

                self.exposure += 1
            
                # Should we count it as a detection, or a rejection? 
                # Only test subjects get de-activated:

                if self.probability < self.rejection_threshold:
                    self.status = 'rejected'
                    if self.kind == 'test':  
                        self.state = 'inactive'
                        self.retirement_time = at_time
                        self.retirement_age = self.exposure

                elif self.probability > self.detection_threshold:
                    self.status = 'detected'
                    if self.kind == 'test':
                        # Let's keep the detections live!
                        #   self.state = 'inactive'
                        #   self.retirement_time = at_time
                        #   self.retirement_age = self.exposure
                        pass

                # Update agent - training history is taken care of elsewhere: 
                if self.kind == 'test':
                     by.testhistory['ID'] = self.ID
                     by.testhistory['I'] = by.contribution

        return

# ----------------------------------------------------------------------
# Plot subject's trajectory, as an overlay on an existing plot:

    def plot_trajectory(self,axes):
    
        plt.sca(axes[0])
        N = np.linspace(0, len(self.trajectory)-1, len(self.trajectory), endpoint=True)
        N[0] = 0.5
        
        if self.kind == 'sim':
            colour = 'blue'
        elif self.kind == 'dud':
            colour = 'red'
        elif self.kind == 'test':
            colour = 'black'
            
        if self.status == 'undecided':
            facecolour = colour
        else:
            facecolour = 'white'
        
        plt.plot(self.trajectory, N, color=colour, alpha=0.1, linewidth=1.0, linestyle="-")
        NN = N[-1]
        if NN > swap.Ncmax: NN = swap.Ncmax
        plt.scatter(self.trajectory[-1], NN, edgecolors=colour, facecolors=facecolour, alpha=0.5)
        
        # if self.kind == 'sim': print self.trajectory[-1], N[-1]
                
        return

# ======================================================================
   
