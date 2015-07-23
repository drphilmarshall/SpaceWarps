# ===========================================================================

import swap

import numpy as np
import pylab as plt
from subject import Ntrajectory
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
      under the MIT license by the Space Warps Science Team.
      http://spacewarps.org/

      2013-04-17  Started: Marshall (Oxford)
    """

# ----------------------------------------------------------------------------

    def __init__(self):

        self.member = {}
        self.probabilities = {'sim':np.array([]), 'dud':np.array([]), 'test':np.array([])}
        self.exposure = {'sim':np.array([]), 'dud':np.array([]), 'test':np.array([])}

        return None

# ----------------------------------------------------------------------------

    def __str__(self):
        return 'collection of %d subjects' % (self.size())

# ----------------------------------------------------------------------------
# Return the number of collection members:

    def size(self):
        return len(self.member)

# ----------------------------------------------------------------------------
# # Return an array giving each samples' exposure to the agents:
#
#     def get_exposure(self):
#
#         N = np.array([])
#         for ID in self.list():
#             subject = self.member[ID]
#             N = np.append(N,subject.exposure)
#
#         self.exposure = N
#         return N
#
# ----------------------------------------------------------------------------
# Return a complete list of collection members:

    def list(self):
        return self.member.keys()

# ----------------------------------------------------------------------------
# Return a list of N collection members, selected at regular intervals. This
# *should* contain a significant number of training subjects, since on average
# 1 in 20 subjects are training...

    def shortlist(self,N,kind='Any',status='Any'):
        reallylonglist = self.list()

        if kind == 'Any' and status == 'Any':
            longlist = reallylonglist
        else:
            longlist = []
            count = 0
            for ID in reallylonglist:
                 subject = self.member[ID]
                 if (kind == 'Any' and subject.status == status) or \
                    (status == 'Any' and subject.kind == kind) or \
                    (kind == subject.kind and subject.status == status):
                     longlist.append(ID)
                     count += 1
            if count < N: N = count

        if N == 0:
            shortlist = []
        else:
            shortlist = longlist[0::int(len(longlist)/N)][0:N]

        return shortlist

# ----------------------------------------------------------------------------
# Get the probability thresholds for this sample:

    def thresholds(self):

        thresholds = {}
        ID = self.shortlist(1)[0]
        subject = self.member[ID]

        thresholds['detection'] = subject.detection_threshold
        thresholds['rejection'] = subject.rejection_threshold

        return thresholds

# ----------------------------------------------------------------------------
# Extract all the lens probabilities of the members of a given kind:

    def collect_probabilities(self,kind):

#       p = np.array([])
#       n = np.array([])
#       for ID in self.list():
#           subject = self.member[ID]
#           if subject.kind == kind:
#               p = np.append(p,subject.probability)
#               n = np.append(n,subject.exposure)
#
#       self.probabilities[kind] = p
#       self.exposure[kind] = n

        # print "Collecting probabilities in a faster way, size:",self.size()
        # Appending wastes a lot of time
        p = np.zeros(self.size())
        n = np.zeros(self.size())
        fill=0
        for ID in self.list():
            subject = self.member[ID]
            if subject.kind == kind:
                p[fill] = subject.mean_probability
                n[fill] = subject.exposure
                fill = fill + 1

        self.probabilities[kind] = p[0:fill]
        self.exposure[kind] = n[0:fill]
        # print "Done collecting probabilities, hopefully faster now, size:",self.size()
        return

# ----------------------------------------------------------------------
# Take stock: how many detections? how many rejections?

    def take_stock(self):

        self.N = 0
        self.Ns = 0
        self.Nt = 0
        self.Ntl = 0
        self.Ntd = 0
        self.Ns_retired = 0
        self.Ns_rejected = 0
        self.Ns_detected = 0
        self.Nt_rejected = 0
        self.Nt_detected = 0
        self.Ntl_rejected = 0
        self.Ntl_detected = 0
        self.Ntd_rejected = 0
        self.Ntd_detected = 0
        self.retirement_ages = np.array([])

        for ID in self.list():
            subject = self.member[ID]
            self.N += 1

            if subject.category == 'training':
                self.Nt += 1
                if subject.kind == 'sim':
                    self.Ntl += 1
                elif subject.kind == 'dud':
                    self.Ntd += 1
            else:
                self.Ns += 1

            # Detected or rejected?
            if subject.status == 'detected':
                if subject.category == 'training':
                    self.Nt_detected += 1
                    if subject.kind == 'sim':
                         self.Ntl_detected += 1
                    elif subject.kind == 'dud':
                         self.Ntd_detected += 1
                else:
                    self.Ns_detected += 1

            elif subject.status == 'rejected':
                if subject.category == 'training':
                    self.Nt_rejected += 1
                    if subject.kind == 'sim':
                        self.Ntl_rejected += 1
                    elif subject.kind == 'dud':
                        self.Ntd_rejected += 1
                else:
                    self.Ns_rejected += 1

            if subject.state  == 'inactive':
                self.Ns_retired += 1
                self.retirement_ages = np.append(self.retirement_ages,subject.retirement_age)

        return

# ----------------------------------------------------------------------
# Make a list of subjects that have been retired during this run:

    def retirementlist(self):

        the_departed = ['none','yet']

        return the_departed


# ----------------------------------------------------------------------
# Prepare to plot subjects' trajectories:

    def start_trajectory_plot(self,final=False,title=None,histogram=True,logscale=True):

        left, width = 0.15, 0.8

        if histogram:
            fig = plt.figure(figsize=(5,8), dpi=300)
            upperarea = [left, 0.4, width, 0.5] # left, bottom, width, height
            lowerarea = [left, 0.1, width, 0.3]
        else:
            fig = plt.figure(figsize=(5,5), dpi=300)
            upperarea = [left, left, width, width] # left, bottom, width, height
            lowerarea = []

        # Upper panel: subjects drifting downwards:

        # First plot an arrow to show the subjects entering the plot.
        # This is non-trivial, you have to overlay in a different
        # set of axes, with linear scales...
        hax = fig.add_axes(upperarea)
        hax.set_xlim(np.log10(swap.pmin),np.log10(swap.pmax))
        hax.set_ylim(np.log10(swap.Ncmax),np.log10(swap.Ncmin))
        for label in hax.get_xticklabels():
            label.set_visible(False)
        for label in hax.get_yticklabels():
            label.set_visible(False)
        for tick in hax.xaxis.get_ticklines():
            tick.set_visible(False)
        for tick in hax.yaxis.get_ticklines():
            tick.set_visible(False)
        plt.sca(hax)
        if logscale:
            plt.arrow(np.log10(2e-4), np.log10(0.3), 0.0, 0.1, fc="k", ec="k", linewidth=2, head_width=0.2, head_length=0.1)
        else:
            plt.arrow(np.log10(2e-4), -0.8, 0.0, 0.1, fc="k", ec="k", linewidth=2, head_width=0.2, head_length=0.1)
        # hax.set_axis_off()

        # Now overlay a transparent frame to plot the subjects in:
        upper = fig.add_axes(upperarea, frameon=False)
        plt.sca(upper)
        upper.set_xlim(swap.pmin,swap.pmax)
        upper.set_xscale('log')
        upper.set_ylim(swap.Ncmax,swap.Ncmin)
        if logscale:
            upper.set_yscale('log')

        # Vertical lines to mark prior and detect/rejection thresholds:
        x = self.thresholds()
        plt.axvline(x=swap.prior,color='gray',linestyle='dotted')
        plt.axvline(x=x['detection'],color='blue',linestyle='dotted')
        plt.axvline(x=x['rejection'],color='red',linestyle='dotted')

        upper.set_ylabel('No. of classifications')
        # Turn off upper panel x labels, if we are plotting a histogram:
        if histogram:
            for label in upper.get_xticklabels():
                label.set_visible(False)

        # Plot title:
        if final:
            upper.set_title('Candidate Trajectories')
        else:
            upper.set_title('Example Subject Trajectories')
        # Manual over-ride:
        if title is not None:
            upper.set_title(title)

        if histogram:
            # Lower panel: histogram:
            lower = fig.add_axes(lowerarea, sharex=upper)
            plt.sca(lower)
            lower.set_xlim(swap.pmin,swap.pmax)
            lower.set_xscale('log')
            lower.set_ylim(0.1,9999)
            # lower.set_yscale('log')
            plt.axvline(x=swap.prior,color='gray',linestyle='dotted')
            plt.axvline(x=x['detection'],color='blue',linestyle='dotted')
            plt.axvline(x=x['rejection'],color='red',linestyle='dotted')
            lower.set_xlabel('Posterior Probability Pr(LENS|d)')
            lower.set_ylabel('No. of subjects')

        else:
            lower = False
            upper.set_xlabel('Posterior Probability Pr(LENS|d)')


        return [upper,lower]

# ----------------------------------------------------------------------
# Prepare to plot subjects' trajectories:

    def finish_trajectory_plot(self,axes,filename,t=None,final=None):

        # If we are not plotting the histogram, the second axis is False...

        if axes[1] is not False:

            # Plot histograms! 0 is the upper panel, 1 the lower.
            plt.sca(axes[1])

            bins = np.linspace(np.log10(swap.pmin),np.log10(swap.pmax),32,endpoint=True)
            bins = 10.0**bins
            colors = ['dimgray','blue','red']
            labels = ['Test: Survey','Training: Sims','Training: Duds']
            thresholds = self.thresholds()

            for j,kind in enumerate(['test','sim','dud']):

                self.collect_probabilities(kind)
                p = self.probabilities[kind]

                # Sometimes all probabilities are lower than pmin!
                # Snap to grid.
                p[p<swap.pmin] = swap.pmin
                # print "kind,bins,p = ",kind,bins,p

                # Final plot - only show subjects above threshold:
                if final:
                    p = p[p>thresholds['rejection']]

                # Pylab histogram:
                plt.hist(p, bins=bins, histtype='stepfilled', color=colors[j], alpha=1.0, label=labels[j])
                plt.legend(prop={'size':10}, framealpha=1.0)

        if t is not None:
            # Add timestamp in top righthand corner:
            plt.sca(axes[0])
            plt.text(1.3*swap.prior,0.27,t,color='gray')

        # Write out to file:
        plt.savefig(filename,dpi=300)

        return

# ======================================================================
