# ===========================================================================

import swap

import numpy as np
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
        know its mean contribution, and other qualities.

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
        self.probabilities = {'LENS':np.array([]), 'NOT':np.array([])}
        self.contributions = np.array([])
        
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
        
# ----------------------------------------------------------------------------
# Extract all the classification probabilities used by the agents:

    def collect_probabilities(self):
    
        PLarray = np.array([])
        PDarray = np.array([])
        contributions = np.array([])
        training = np.array([])
        for ID in self.list():
            classifier = self.member[ID]
            PLarray = np.append(PLarray,classifier.PL)
            PDarray = np.append(PDarray,classifier.PD)
            contributions = np.append(contributions,classifier.contribution)
            training = np.append(training,classifier.NL+classifier.ND)

        self.probabilities['LENS'] = PLarray
        self.probabilities['NOT'] = PDarray
        self.contributions = contributions
        self.training = training

        return
        
# ----------------------------------------------------------------------
# Prepare to plot classifiers' histories:

    def start_history_plot(self):
        
        Nmin = 0.5
        Nmax = 2000.0
        
        bins = np.linspace(np.log10(Nmin),np.log10(Nmax),20,endpoint=True)
        self.collect_probabilities()
        logN = np.log10(self.training)
        
        fig = plt.figure(figsize=(6,5), dpi=300)

        # Linear xes for histogram:
        hax = fig.add_axes([0.15,0.15,0.85,0.80])
        hax.set_xlim(np.log10(Nmin),np.log10(Nmax))
        hax.set_ylim(0.0,0.5*len(logN))
        for label in hax.get_xticklabels():
            label.set_visible(False)
        for label in hax.get_yticklabels():
            label.set_visible(False)
            
        plt.hist(logN, bins=bins, histtype='stepfilled', color='yellow', alpha=0.4)
            
 
        # Logarithmic axes for information contribution plot: 
        axes = fig.add_axes([0.15,0.15,0.85,0.80], frameon=False)
        axes.set_xlim(Nmin,Nmax)
        axes.set_xscale('log')
        axes.set_ylim(0.0,1.0)
        axes.set_xticks([1,10,100,1000])
        axes.set_yticks([0.0,0.2,0.4,0.6,0.8,1.0])
        axes.set_xlabel('No. of training subjects classified')
        axes.set_ylabel('Contributed information per classification (bits)')
        axes.set_title('Classifier Histories')
        
        return axes

# ----------------------------------------------------------------------
# Prepare to plot classifiers' histories:

    def finish_history_plot(self,axes,filename):
    
        plt.sca(axes)
        plt.savefig(filename,dpi=300)
            
        return

# ----------------------------------------------------------------------
# Plot histograms of classifiers' confusion matrix element probabilities:

    def plot_histogram(self,filename):
    
        fig = plt.figure(figsize=(6,6), dpi=300)

        width,height,margin = 0.65,0.2,0.1
        scatterarea   = [margin, margin+height, width, width] # left, bottom, width, height
        righthistarea = [margin+width, margin+height, height, width]
        lowerhistarea = [margin, margin, width, height]

        scatter = fig.add_axes(scatterarea)
        righthist = fig.add_axes(righthistarea, sharey=scatter)
        lowerhist = fig.add_axes(lowerhistarea, sharex=scatter)

        pmin,pmax = 0.0,1.0
        self.collect_probabilities()
        
        # Add a little bit of scatter to the probabilities, to make
        # the ones near (0.5,0.5) visible:
        PD = self.probabilities['NOT']
        PD += 4.0*(1.0-PD)*PD*0.01*np.random.randn(len(PD))
        PL = self.probabilities['LENS']
        PL += 4.0*(1.0-PL)*PL*0.01*np.random.randn(len(PL))
        
        bins = np.linspace(0.0,1.0,20,endpoint=True)

        # Scatter plot:
        plt.sca(scatter)
        scatter.set_xlim(pmin,pmax)
        scatter.set_ylim(pmin,pmax)
        plt.axvline(0.5,color='gray',linestyle='dotted')
        plt.axhline(0.5,color='gray',linestyle='dotted')
        scatter.set_ylabel('Pr("NOT"|NOT)')
        for label in scatter.get_xticklabels():
            label.set_visible(False)
        scatter.set_title('Classifier Probabilities')
        plt.text(0.02,0.02,'"Obtuse"',color='gray')
        plt.text(0.02,0.96,'"Pessimistic"',color='gray')
        plt.text(0.74,0.02,'"Optimistic"',color='gray')
        plt.text(0.81,0.96,'"Astute"',color='gray')
        
        # Training received:
        size = 4*self.training + 6.0
        plt.scatter(PL, PD, s=size, color='yellow', alpha=0.5)
        
        # Information contributed:
        size = 200*self.contributions + 3.0
        plt.scatter(PL, PD, s=size, color='green', alpha=0.5)

        # Right histogram panel: 
        plt.sca(righthist)
        righthist.set_ylim(pmin,pmax)
        righthist.set_xlim(0.5*len(PD),0.0)
        plt.axhline(0.5,color='gray',linestyle='dotted')
        for label in righthist.get_yticklabels():
            label.set_visible(False)
        for label in righthist.get_xticklabels():
            label.set_visible(False)
           
        plt.hist(PD, bins=bins, orientation='horizontal', histtype='stepfilled', color='red', alpha=0.7)


        # Lower histogram panel: 
        plt.sca(lowerhist)
        lowerhist.set_xlim(pmin,pmax)
        lowerhist.set_ylim(0.0,0.5*len(PL))
        plt.axvline(0.5,color='gray',linestyle='dotted')
        for label in lowerhist.get_yticklabels():
            label.set_visible(False)
        lowerhist.set_xlabel('Pr("LENS"|LENS)')
           
        plt.hist(PL, bins=bins, histtype='stepfilled', color='blue', alpha=0.7)


        plt.savefig(filename,dpi=300)
        
        return


# ======================================================================
   
