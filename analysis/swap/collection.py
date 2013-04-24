# ===========================================================================

import swap

import numpy as np
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
        self.probabilities = {'sim':np.array([]), 'dud':np.array([]), 'test':np.array([])}
                
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
        
# ----------------------------------------------------------------------------
# Extract all the lens probabilities of the members of a given kind:

    def collect_probabilities(self,kind):
    
        p = np.array([])
        for ID in self.list():
            subject = self.member[ID]
            if subject.kind == kind:
                p = np.append(p,subject.probability)
        
        self.probabilities[kind] = p
        
        return
        
# ----------------------------------------------------------------------
# Prepare to plot subjects' trajectories. We need t

    def start_trajectory_plot(self):
    
        fig = plt.figure(figsize=(5,8), dpi=300)

        left, width = 0.15, 0.8
        upperarea = [left, 0.4, width, 0.5]# left, bottom, width, height
        lowerarea = [left, 0.1, width, 0.3]

        upper = fig.add_axes(upperarea)
        lower = fig.add_axes(lowerarea, sharex=upper)

        # Upper panel: subjects drifting downwards:
        plt.sca(upper)
        upper.set_xlim(1e-8,1.0)
        upper.set_xscale('log')
        upper.set_ylim(200.0,0.5)
        upper.set_yscale('log')
        plt.axhline(y=5.5,color='gray',linestyle='dotted')
        plt.axvline(x=0.3,color='blue',linestyle='dotted')
        plt.axvline(x=1e-5,color='red',linestyle='dotted')
        upper.set_ylabel('No. of classifications')
        for label in upper.get_xticklabels():
            label.set_visible(False)
        upper.set_title('Subject Trajectories')
        
        # Lower panel: histograms:
        plt.sca(lower)
        lower.set_xlim(1e-8,1.0)
        lower.set_xscale('log')
        lower.set_ylim(0.1,199)
        # lower.set_yscale('log')
        plt.axvline(x=0.3,color='blue',linestyle='dotted')
        plt.axvline(x=1e-5,color='red',linestyle='dotted')
        lower.set_xlabel('Posterior Probability Pr(LENS|d)')
        lower.set_ylabel('No. of subjects')
           
        return [upper,lower]

# ----------------------------------------------------------------------
# Prepare to plot subjects' trajectories:

    def finish_trajectory_plot(self,axes,filename):
    
        # Plot histograms! 0 is the upper panel, 1 the lower.
        plt.sca(axes[1])
        
        bins = np.linspace(np.log10(1e-8),np.log10(1.0),32,endpoint=True)
        bins = 10.0**bins
        colors = ['blue','red','black']
        labels = ['Sims','Duds','Survey']
        
        for j,kind in enumerate(['sim','dud','test']):
            
            self.collect_probabilities(kind)
            p = self.probabilities[kind]

            # Numpy histogram:
            # h,x = np.histogram(p,bins=bins,range=[bins[0],bins[-1]])
            # plt.plot(x[:-1],h,drawstyle='steps',color=colors[j])  
            
            # Pylab histogram:
            plt.hist(p, bins=bins, histtype='stepfilled', color=colors[j], alpha=0.7, label=labels[j])
            plt.legend()
                   
        # Write out to file:
        plt.savefig(filename,dpi=300)
            
        return

# ======================================================================
   
