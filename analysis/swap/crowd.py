# ===========================================================================

import swap

import pylab as plt

# ======================================================================

class Crowd(object):
    """
    NAME
        Crowd

    PURPOSE
        Represent a group of volunteers by assigning each one an agent.

    COMMENTS
        The members of a Crowd are all agents known as Classifiers. 
        The Crowd knows how big it is, and could, in principle, also 
        know its mean expertise, and other qualities.

    INITIALISATION
        From scratch.
    
    METHODS AND VARIABLES
        Crowd.member(Name)         The agent assigned to Name
        Crowd.list                 The Names of the Crowd's members
        Crowd.size()               The size of the Crowd
        Crowd.start_history_plot()
        Crowd.finish_history_plot()
        
    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-17  Started Marshall (Oxford)
    """

# ----------------------------------------------------------------------------

    def __init__(self):
        self.member = {}
        return None

# ----------------------------------------------------------------------------

    def __str__(self):
        return 'crowd of %d classification agents' % (self.size())       
        
# ----------------------------------------------------------------------------

    def size(self):
        return len(self.member)
        
# ----------------------------------------------------------------------------

    def list(self):
        return self.member.keys()
        
# ----------------------------------------------------------------------
# Prepare to plot classifiers' histories:

    def start_history_plot(self):
    
        plt.figure()
        axes = plt.gca()
        axes.set_xlim(0.5,1000.0)
        axes.set_xscale('log')
        axes.set_ylim(0.0,1.0)
        axes.set_xticks([1,10,100,2000])
        axes.set_yticks([0.0,0.2,0.4,0.6,0.8,1.0])
        axes.set_xlabel('No. of training subjects classified')
        axes.set_ylabel('Information per classification (bits)')
            
        return axes

# ----------------------------------------------------------------------
# Prepare to plot classifiers' histories:

    def finish_history_plot(self,axes,filename):
    
        plt.sca(axes)
        plt.savefig(filename,dpi=300)
            
        return

# ======================================================================
   
