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
        it knows its state (which is different according to category).
        Each subject (regardless of category) has a probability of 
        being a LENS, and this is tracked along a trajectory.
        
        Test subject states:
          * Active    Still being classified:     P < ceiling
          * Promoted  Still being classified:     P > ceiling
          * Retired   No longer being classified: P < floor
          
        Training subject states:
          * LENS      It actually is a LENS
          * NOT       It actually is NOT a LENS
        
        
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

    def __init__(self,name,category,kind=None):
        self.name = name
        self.category = category

        if category == 'test':
            self.state = 'Active'
        if category == 'training':
            self.state = kind
            
        if self.state is None: 
           raise Exception("SWAP Subject: unkindness. Name, category = "+name+", "+category)    
        
        self.probability = prior
        
        self.trajectory = np.array([self.probability])
        
        return None

# ----------------------------------------------------------------------

    def __str__(self):
        return 'individual subject named %s, Pr(LENS|d) = %.2f' % \
               (self.name,self.probability)       
        
# ----------------------------------------------------------------------
# Update probability of LENS, given latest classification:
#   eg.  sample.member[ID].described(by=classifier,as_kind='LENS')

    def described(self,by=None,as_kind=None):

        if by==None or as_kind==None:
            pass

        else:
            if as_kind=='LENS':
                likelihood = by.PL
                likelihood /= (by.PL*self.probability + (1-by.PD)*(1-self.probability))
            elif as_kind=='NOT':
                likelihood = (1-by.PL)
                likelihood /= ((1-by.PL)*self.probability + by.PD*(1-self.probability))
            else:
                raise Exception("Apparently, the subject was a "+as_kind)

            self.probability = likelihood*self.probability
            
            self.trajectory = np.append(self.trajectory,self.probability)

        return

# ----------------------------------------------------------------------
# Plot subject's trajectory, as an overlay on an existing plot:

    def plot_trajectory(self,axes):
    
        plt.sca(axes)
        N = np.linspace(1, len(self.trajectory), len(self.trajectory), endpoint=True)
        
        if self.state=='LENS':
            colour = 'blue'
        elif self.state=='NOT':
            colour = 'red'
        else:
            colour = 'black'
        
        plt.plot(N, self.trajectory, color=colour, alpha=0.1, linewidth=1.0, linestyle="-")
        plt.scatter(N[-1], self.trajectory[-1], color=colour, alpha=0.5)
        
        return

# ======================================================================
   
