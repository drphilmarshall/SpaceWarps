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
    
        plt.figure(figsize=(5,8), dpi=100)
        axes = plt.gca()
        axes.set_aspect(3.0)
        axes.set_xlim(1e-8,1.0)
        axes.set_xscale('log')
        axes.set_ylim(200.0,0.5)
        axes.set_yscale('log')
        plt.axvline(x=0.3,color='blue',linestyle='dotted')
        plt.axvline(x=1e-5,color='red',linestyle='dotted')
        axes.set_ylabel('No. of classifications')
        axes.set_xlabel('Posterior Probability Pr(LENS|d)')
        axes.set_title('Subject Trajectories')
            
        return axes

# ----------------------------------------------------------------------
# Prepare to plot subjects' trajectories:

    def finish_trajectory_plot(self,axes,filename):
    
        plt.sca(axes)
        plt.savefig(filename,dpi=300)
            
        return

# ======================================================================
   
