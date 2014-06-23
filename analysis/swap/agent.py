"""
TODO:
    Save the list of clicks!
"""

# ======================================================================

import swap

import numpy as np
import pylab as plt

# ======================================================================

actually_it_was_dictionary = {'LENS': 1, 'NOT': 0, 'UNKNOWN': -1}

class Agent(object):
    """
    NAME
        Agent

    PURPOSE
        A little robot who will interpret the classifications of an
        individual volunteer.

    COMMENTS
        An Agent is assigned to represent a  volunteer, whose Name is
        either a Zooniverse userid or, if that is not available, an IP
        address. Agents each have a History of N classifications,
        including ND that turned out to be duds and NL that turned out
        to be lenses. NT is the total number of training subjects
        classified, and is equal to N in the simple "LENS or NOT"
        analysis. Each Agent carries a "confusion matrix"
        parameterised by two numbers, PD and PL, the meaning of which is
        as follows:

        An Agent assumes that its volunteer says:

        | "LENS" when it is NOT    "LENS" when it is a LENS  |
        | with probability (1-PD)    with probability PL     |
        |                                                    |
        | "NOT" when it is NOT     "NOT" when it is a LENS   |
        | with probability PD        with probability (1-PL) |

        It makes the simplest possible assignment for these probabilities,
        namely that PX = 0.5 if NX = 0, and then updates from there using the
        training subjects such that
          PX = (NX_correct + initialNX/2) / (NX+initialNX)
        at all times. For example, if the volunteer is right about 80% of the
        simulated lenses they see, the agent will assign:
          PL = Pr("LENS"|LENS) = 0.8.
        initialNX are listed in the configuration file.

        Agents are initialised with PL = PD = some initial value,
        provided in the configuration file. (0.5,0.5) would be a
        conservative choice - but it may well underestimate the
        volunteers' natural lens-spotting talent. PL and PD are capped
        because the agents assume that their volunteers are
        only human. The upper limits are kept in swap.PDmax and
        swap.PLmax.

        The big assumption the Agent is making is that its
        volunteer has a single, constant PL and a single, constant
        PD, which it estimates using all the volunteer's data. This is
        clearly sub-optimal, but might be good enough for a first
        attempt. We'll see!


    INITIALISATION
        name

    METHODS
        Agent.update_contribution()  Calculate the expected
                                          information contributed
                                          per classification
        Agent.heard(it_was=X,actually_it_was=Y)     Read report.
        Agent.plot_history(axes)

    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-17:  Started Marshall (Oxford)
    """

# ----------------------------------------------------------------------

    def __init__(self,name,pars):
        self.name = name
        self.PD = pars['initialPD']
        self.PL = pars['initialPL']
        self.ND = 2 + pars['skepticism']
        self.NL = 2 + pars['skepticism']
        self.N = 0
        self.NT = 0
        # back-compatibility:
        self.contribution = 0.0*self.update_skill() # This call also sets self.skill, internally
        self.traininghistory = {'ID':'tutorial', 'Skill':np.array([self.skill]), 'PL':np.array([self.PL]), 'PD':np.array([self.PD]), 'ItWas':np.array([], dtype=int), 'ActuallyItWas':np.array([], dtype=int)}
        self.testhistory = {'ID':[], 'I':np.array([]), 'Skill':np.array([]), 'ItWas':np.array([], dtype=int)}

        return None

# ----------------------------------------------------------------------

    def __str__(self):
        return 'individual classification agent representing %s with contribution %.2f' % \
               (self.name,self.contribution)

# ----------------------------------------------------------------------
# Compute expected information per classification:

    def update_skill(self):

        ## plogp = np.zeros([2])
        ## plogp[0] = 0.5*(self.PD+self.PL)*np.log2(self.PD+self.PL)
        ## plogp[1] = 0.5*(1.0-self.PD+1.0-self.PL)*np.log2(1.0-self.PD+1.0-self.PL)
        ## self.contribution = np.sum(plogp)

        self.skill = swap.expectedInformationGain(0.5, self.PL, self.PD)

        return self.skill

# ----------------------------------------------------------------------
# Update confusion matrix with latest result:
#   eg.  collaboration.member[Name].heard(it_was='LENS',actually_it_was='NOT',with_probability=P,ignore=False)

    def heard(self,it_was=None,actually_it_was=None,with_probability=1.0,ignore=False):

        if it_was==None or actually_it_was==None:
            pass

        else:
            if not ignore:
                        
                if actually_it_was=='LENS':
                    self.PL = (self.PL*self.NL + (it_was==actually_it_was))/(1+self.NL)
                    self.PL = np.min([self.PL,swap.PLmax])
                    self.PL = np.max([self.PL,swap.PLmin])
                    self.NL += 1
                    self.NT += 1

                elif actually_it_was=='NOT':
                    self.PD = (self.PD*self.ND + (it_was==actually_it_was))/(1+self.ND)
                    self.PD = np.min([self.PD,swap.PDmax])
                    self.PD = np.max([self.PD,swap.PDmin])
                    self.ND += 1
                    self.NT += 1

                # Unsupervised learning! Mad if this actually works.
                elif actually_it_was=='UNKNOWN':
                    
                    increment = with_probability

                    if it_was=='LENS':
                    
                        self.PL = (self.PL*self.NL + increment)/(self.NL + increment)
                        self.PL = np.min([self.PL,swap.PLmax])
                        self.PL = np.max([self.PL,swap.PLmin])
                        self.NL += increment

                        self.PD = (self.PD*self.ND +       0.0)/(self.ND + (1.0-increment))
                        self.PD = np.min([self.PD,swap.PDmax])
                        self.PD = np.max([self.PD,swap.PDmin])
                        self.ND += (1.0 - increment)
                    
                    elif it_was=='NOT':
                    
                        self.PL = (self.PL*self.NL +       0.0)/(self.NL + increment)
                        self.PL = np.min([self.PL,swap.PLmax])
                        self.PL = np.max([self.PL,swap.PLmin])
                        self.NL += increment

                        self.PD = (self.PD*self.ND + (1.0-increment))/(self.ND + (1.0-increment))
                        self.PD = np.min([self.PD,swap.PDmax])
                        self.PD = np.max([self.PD,swap.PDmin])
                        self.ND += (1.0 - increment)
                    
                    # self.NT += 1 # Don't count test images as training images!

                else:
                    raise Exception("Apparently, the subject was actually a "+str(actually_it_was))

            # Always log progress, even if not learning:
            self.traininghistory['Skill'] = np.append(self.traininghistory['Skill'],self.update_skill())
            self.traininghistory['PL'] = np.append(self.traininghistory['PL'],self.PL)
            self.traininghistory['PD'] = np.append(self.traininghistory['PD'],self.PD)

            self.traininghistory['ItWas'] = np.append(self.traininghistory['ItWas'], actually_it_was_dictionary[it_was])
            self.traininghistory['ActuallyItWas'] = np.append(self.traininghistory['ActuallyItWas'], actually_it_was_dictionary[actually_it_was])

        return

# ----------------------------------------------------------------------
# Plot agent's history, as an overlay on an existing plot:

    def plot_history(self,axes):

        plt.sca(axes)
        I = self.traininghistory['Skill']
        N = np.linspace(1, len(I), len(I), endpoint=True)

        # Information contributions:
        plt.plot(N, I, color="green", alpha=0.2, linewidth=2.0, linestyle="-")
        plt.scatter(N[-1], I[-1], color="green", alpha=0.5)

        return

# ----------------------------------------------------------------------
# Get a realization for agent's PL distribution

    def get_PL_realization(self,Ntrajectory):
        NL_correct=self.PL*self.NL;
        NL_correct_realize=np.random.binomial(self.NL,self.PL,size=Ntrajectory);
        PL_realize=(NL_correct_realize*1.0)/(self.NL);
        idx=np.where(PL_realize>swap.PLmax);
        PL_realize[idx]=swap.PLmax;
        idx=np.where(PL_realize<swap.PLmin);
        PL_realize[idx]=swap.PLmin;
        #print NL_correct,NL_correct_realize,PL_realize
        return PL_realize;

# ----------------------------------------------------------------------
# Get a realization for agent's PD distribution

    def get_PD_realization(self,Ntrajectory):
        ND_correct=self.PD*self.ND;
        ND_correct_realize=np.random.binomial(self.ND,self.PD,size=Ntrajectory);
        PD_realize=(ND_correct_realize*1.0)/(self.ND);
        idx=np.where(PD_realize>swap.PDmax);
        PD_realize[idx]=swap.PDmax;
        idx=np.where(PD_realize<swap.PDmin);
        PD_realize[idx]=swap.PDmin;
        #print  ND_correct,ND_correct_realize,PD_realize
        return PD_realize;

# ======================================================================
