# ===========================================================================

import swap

import numpy as np
import pylab as plt

# ======================================================================

class Bureau(object):
    """
    NAME
        Bureau

    PURPOSE
        A group of agents assigned to represent the volunteers.

    COMMENTS
        The members of a Bureau are all Agents.  The Bureau knows how
        big it is, and also holds a summary of its agents' 
        classifiers' information contributions.

    INITIALISATION
        From scratch.
    
    METHODS AND VARIABLES
        Bureau.member(Name)         The agent assigned to Name
        Bureau.list                 The Names of the Bureau's members
        Bureau.size()               The size of the Bureau
        Bureau.start_history_plot()
        Bureau.finish_history_plot()
        
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
        return 'bureau of %d classification agents' % (self.size())       
        
# ----------------------------------------------------------------------------
# Return the number of bureau members:

    def size(self):
        return len(self.member)
        
# ----------------------------------------------------------------------------
# Return a complete list of bureau members:

    def list(self):
        return self.member.keys()
        
# ----------------------------------------------------------------------------
# Return a list of N bureau members, selected at regular intervals:

    def shortlist(self,N):
        longlist = self.list()
        return longlist[0::int(len(longlist)/N)][0:N]
            
# ----------------------------------------------------------------------------
# Extract all the classification probabilities used by the agents:

    def collect_probabilities(self):
    
        PLarray = np.array([])
        PDarray = np.array([])
        contributions = np.array([])
        skills = np.array([])
        Ntraining = np.array([])
        Ntotal = np.array([])
        for ID in self.list():
            agent = self.member[ID]
            PLarray = np.append(PLarray,agent.PL)
            PDarray = np.append(PDarray,agent.PD)
            contributions = np.append(contributions,agent.contribution)
            skills = np.append(skills,agent.skill)
            Ntraining = np.append(Ntraining,agent.NT)
            Ntotal = np.append(Ntotal,agent.N)  # Nc

        self.probabilities['LENS'] = PLarray
        self.probabilities['NOT'] = PDarray
        self.contributions = contributions
        self.skills = skills
        self.Ntraining = Ntraining
        self.Ntotal = Ntotal
        self.Ntest = Ntotal - Ntraining

        return
        
# ----------------------------------------------------------------------
# Prepare to plot agents' histories:

    def start_history_plot(self):
        
        Nmin = 0.5
        Nmax = 2000.0
        
        bins = np.linspace(np.log10(Nmin),np.log10(Nmax),20,endpoint=True)
        self.collect_probabilities()
        logN = np.log10(self.Ntraining)
        
        fig = plt.figure(figsize=(6,5), dpi=300)

        # Linear xes for histogram:
        hax = fig.add_axes([0.15,0.15,0.85,0.80])
        hax.set_xlim(np.log10(Nmin),np.log10(Nmax))
        hax.set_ylim(0.0,0.5*len(logN))
        for label in hax.get_xticklabels():
            label.set_visible(False)
        for label in hax.get_yticklabels():
            label.set_visible(False)
        for tick in hax.xaxis.get_ticklines(): 
            tick.set_visible(False) 
        for tick in hax.yaxis.get_ticklines(): 
            tick.set_visible(False) 
            
        plt.hist(logN, bins=bins, histtype='stepfilled', color='yellow', alpha=0.5)
            
 
        # Logarithmic axes for information contribution plot: 
        axes = fig.add_axes([0.15,0.15,0.85,0.80], frameon=False)
        axes.set_xlim(Nmin,Nmax)
        axes.set_xscale('log')
        axes.set_ylim(0.0,1.0)
        plt.axhline(y=swap.Imax,color='gray',linestyle='dotted')
        axes.set_xlabel('No. of training subjects classified')
        axes.set_ylabel('Contributed information per classification (bits)')
        axes.set_title('Example Agent Histories')
        
        return axes

# ----------------------------------------------------------------------
# Prepare to plot agents' histories:

    def finish_history_plot(self,axes,t,filename):
    
        plt.sca(axes)
        
        # Timestamp:
        plt.text(100,swap.Imax+0.02,t,color='gray')
       
        plt.savefig(filename,dpi=300)
            
        return

# ----------------------------------------------------------------------
# Plot scattergraph and histograms of agents' confusion matrix 
# element probabilities:

    def plot_probabilities(self,Nc,t,filename):
    
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
        
        # Only plot a shortlist of 200, or fewer, uniformly sampled:
        TheseFewNames = self.shortlist(np.min([Nc,self.size()]))
        index = [i for i,Name in enumerate(self.list()) if Name in set(TheseFewNames)]
        PD = self.probabilities['NOT'][index]
        PL = self.probabilities['LENS'][index]
        I = self.contributions[index]
        S = self.skills[index]
        NT = self.Ntraining[index]
        
        # Add a little bit of scatter to the probabilities, to make
        # the ones near the starting point visible:
        PD += 4.0*(1.0-PD)*PD*0.005*np.random.randn(len(PD))
        PL += 4.0*(1.0-PL)*PL*0.005*np.random.randn(len(PL))
        
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
        scatter.set_title('Example Agent Probabilities')
        plt.text(0.02,0.02,'"Obtuse"',color='gray')
        plt.text(0.02,0.96,'"Pessimistic"',color='gray')
        plt.text(0.74,0.02,'"Optimistic"',color='gray')
        plt.text(0.81,0.96,'"Astute"',color='gray')
        plt.text(0.15,0.87,'"Random classifier"',color='gray',rotation=-45)

        # Plot the random classifier line
        plt.plot(np.arange(2),1-np.arange(2),color='grey');
        
        # Training received:
        size = 4*NT + 6.0
        plt.scatter(PL, PD, s=size, color='yellow', alpha=0.5)
        
        # # Information contributed (summed skill):
        # size = 4*I + 3.0
        # plt.scatter(PL, PD, s=size, color='green', alpha=0.5)

        # Information contributed per classification (skill):
        size = 200*S + 3.0
        plt.scatter(PL, PD, s=size, color='green', alpha=0.5)


        # For the histograms use all the information available
        PD=self.probabilities['NOT']
        PL=self.probabilities['LENS']

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

        # Timestamp:
        plt.text(0.03,0.82*0.5*len(PL),t,color='gray')

        plt.savefig(filename,dpi=300)
        
        return


# ======================================================================
   
