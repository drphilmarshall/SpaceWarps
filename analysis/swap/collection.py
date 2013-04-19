# ===========================================================================

import swap

import pylab as plt

# ======================================================================

class Collection(object):
    """
    NAME
        Collection

    PURPOSE
        Model a collection of subjects.

    COMMENTS
        All subjects in a Collection are all Zooniverse subjects. 

    INITIALISATION
        From scratch.
    
    METHODS
        Collection.member(Name)     Returns the Subject called Name
        Collection.size()           Returns the size of the Collection
        Collection.list()           Returns the IDs of the members
        
    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    trajectorY
      2013-04-17  Started Marshall (Oxford)
    """

# ----------------------------------------------------------------------------

    def __init__(self):
        self.member = {}
        return None

# ----------------------------------------------------------------------------

    def __str__(self):
        return 'collection of %d subjects' % (self.size())       
        
# ----------------------------------------------------------------------------

    def size(self):
        return len(self.member)
        
# ----------------------------------------------------------------------------

    def list(self):
        return self.member.keys()
        
# ----------------------------------------------------------------------
# Prepare to plot subjects' trajectories:

    def start_trajectory_plot(self):
    
        plt.figure()
        axes = plt.gca()
        axes.set_xlim(0.5,2000.0)
        axes.set_xscale('log')
        axes.set_ylim(0.00001,1.0)
        axes.set_yscale('log')
        axes.set_xticks([1,10,100,2000])
        axes.set_yticks([0.00001,0.0001,0.001,0.01,0.1,1.0])
        axes.set_xlabel('No. of classifications')
        axes.set_ylabel('Posterior Probability Pr(LENS|d)')
        axes.set_title('Subject Trajectories')
            
        return axes

# ----------------------------------------------------------------------
# Prepare to plot subjects' trajectories:

    def finish_trajectory_plot(self,axes,filename):
    
        plt.sca(axes)
        plt.savefig(filename,dpi=300)
            
        return

# ======================================================================
   
