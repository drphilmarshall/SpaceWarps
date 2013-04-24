# ======================================================================

import swap

import numpy as np
import pylab as plt

# Every subject starts with the following probability of being a LENS:
prior = 0.0002

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
        
        Subject states:
          * active    Still being classified:     P < ceiling
          * promoted  Still being classified:     P > ceiling
          * retired   No longer being classified: P < floor
        Training subjects are always active. Retired = inactive.
        
        Subject kinds:
          * test      A subject from the test (random, survey) set
          * sim       A training subject containing a simulated lens
          * dud       A training subject known not to contain any lenses
        
        Subject truths:
          * LENS      It actually is a LENS (sim)
          * NOT       It actually is NOT a LENS (dud)
          * UNKNOWN   It could be either (test)

        
    INITIALISATION
        name
    
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

    def __init__(self,name,category,kind,truth):

        self.name = name
        self.category = category
        self.kind = kind
        self.truth = truth

        self.state = 'active'
            
        self.probability = prior
        
        self.trajectory = np.array([self.probability])
        
        return None

# ----------------------------------------------------------------------

    def __str__(self):
        return 'individual (%s) subject named %s, Pr(LENS|d) = %.2f' % \
               (self.kind,self.name,self.probability)       
        
# ----------------------------------------------------------------------
# Update probability of LENS, given latest classification:
#   eg.  sample.member[ID].was_described(by=classifier,as_being='LENS')

    def was_described(self,by=None,as_being=None):

        if by==None or as_being==None:
            pass

        else:
            if as_being == 'LENS':
                likelihood = by.PL
                likelihood /= (by.PL*self.probability + (1-by.PD)*(1-self.probability))
            
            elif as_being == 'NOT':
                likelihood = (1-by.PL)
                likelihood /= ((1-by.PL)*self.probability + by.PD*(1-self.probability))
            
            else:
                raise Exception("Unrecognised classification result: "+as_being)

            self.probability = likelihood*self.probability
            
            self.trajectory = np.append(self.trajectory,self.probability)

        return

# ----------------------------------------------------------------------
# Plot subject's trajectory, as an overlay on an existing plot:

    def plot_trajectory(self,axes):
    
        plt.sca(axes)
        N = np.linspace(1, len(self.trajectory), len(self.trajectory), endpoint=True)
        
        if self.kind == 'sim':
            colour = 'blue'
        elif self.kind == 'dud':
            colour = 'red'
        elif self.kind == 'test':
            colour = 'black'
        
        plt.plot(N, self.trajectory, color=colour, alpha=0.1, linewidth=1.0, linestyle="-")
        plt.scatter(N[-1], self.trajectory[-1], color=colour, alpha=0.5)
        
        return

# ======================================================================
   
