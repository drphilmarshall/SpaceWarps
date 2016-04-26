# ======================================================================

import swap

import numpy as np
import pylab as plt

# Every subject starts with the following probability of being a LENS:
prior = 2e-4

# Every subject starts 50 trajectories. This will slow down the code,
# but its ok, we can always parallelize
Ntrajectory=50
# This should really be a user-supplied constant, in the configuration.

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

        Subject state:
          * active    Still being classified
          * inactive  No longer being classified
        Training subjects are always active. Retired = inactive.

        Subject status:
          * detected  P > detection_threshold
          * rejected  P < rejection_threshold
          * undecided otherwise

        Subject categories:
          * test      A subject from the test (random, survey) set
          * training  A training subject, either a sim or a dud

        Subject kinds:
          * test      A subject from the test (random, survey) set
          * sim       A training subject containing a simulated lens
          * dud       A training subject known not to contain any lenses

        Subject truths:
          * LENS      It actually is a LENS (sim)
          * NOT       It actually is NOT a LENS (dud)
          * UNKNOWN   It could be either (test)

        CPD 23 June 2014:
        Each subject also has an annotationhistory, which keeps track of who
        clicked, what they said it was, where they clicked, and their ability
        to tell a lens (PL) and a dud (PD)

    INITIALISATION
        ID

    METHODS
        Subject.described(by=X,as=Y)     Calculate Pr(LENS|d) given
                                         classifier X's assessment Y
        Subject.plot_trajectory(axes)

    BUGS


    FEATURE REQUESTS
        Figure out how to let there be multiple lenses in a subject...


    AUTHORS
      This file is part of the Space Warps project, and is distributed
      under the MIT license by the Space Warps Science Team.
      http://spacewarps.org/

    trajectory
      2013-04-17  Started Marshall (Oxford)
      2013-05-15  Surhud More (KIPMU)
    """

# ----------------------------------------------------------------------

    def __init__(self,ID,ZooID,category,kind,flavor,truth,thresholds,location,prior=2e-4):

        self.ID = ID
        self.ZooID = ZooID
        self.category = category
        self.kind = kind
        self.flavor = flavor
        self.truth = truth

        self.state = 'active'
        self.status = 'undecided'

        self.retirement_time = 'not yet'
        self.retirement_age = 0.0

        self.probability = np.zeros(Ntrajectory)+prior
        self.mean_probability = prior
        self.median_probability = prior
        self.trajectory = np.zeros(Ntrajectory)+self.probability;
        self.exposure = 0

        self.detection_threshold = thresholds['detection']
        self.rejection_threshold = thresholds['rejection']

        self.location = location

        self.annotationhistory = {'Name': np.array([]),
                            'ItWas': np.array([], dtype=int),
                            'PL': np.array([]),
                            'PD': np.array([]),
                            'At_X': [],
                            'At_Y': [],
                            'At_Time': []}

        return None

# ----------------------------------------------------------------------

    def __str__(self):
        # Calculate the mean probability and the error on it
        mean_logp =sum(np.log(self.probability))/Ntrajectory
        error_logp=sum((np.log(self.probability)-mean_logp)**2/Ntrajectory)
        return 'individual (%s) subject, ID %s, Pr(LENS|d) = %.2f \pm %.2f' % \
               (self.kind,self.ID,np.exp(mean_logp),np.exp(mean_logp)*error_logp)

# ----------------------------------------------------------------------
# Update probability of LENS, given latest classification:
#   eg.  sample.member[ID].was_described(by=agent,as_being='LENS',at_time=t)

    def was_described(self,by=None,as_being=None,at_time=None,while_ignoring=0,haste=False,at_x=[-1],at_y=[-1],online=True,record=True,realize_confusion=True,laplace_smoothing=0):

        # TODO: CPD: make likelihood into an attribute?  if so, I need to
        # probably wipe it here to avoid silent bugs (likelihood not updating,
        # etc)

        # Rename some variables:
        a_few_at_the_start = while_ignoring

        if online:
            # Update agent:
            by.N += 1

        if by==None or as_being==None or by.kind == 'banned':
            pass

        # Optional: skip straight past inactive subjects.
        # It would be nice to warn the user that inactive subjects
        # should not be being classified:  this can happen if the
        # subject has not been cleanly retired  in the Zooniverse
        # database. However, this leads to a huge  stream of warnings,
        # so best not do that... Note also that training subjects
        # cannot go inactive - but we need to ignore classifications of
        # them after they cross threshold, for the training set to
        # be useful in giving us the selection function. What you see in
        # the trajectory plot is the *status* of the training subjects,
        # not their *state*.

        elif haste and (     self.state == 'inactive' \
                         or self.status == 'detected' \
                         or self.status == 'rejected' ):

                # print "SWAP: WARNING: subject "+self.ID+" is inactive, but appears to have been just classified"
                pass

        else:

            # update the annotation history
            if record:
                as_being_dict = {'LENS': 1, 'NOT': 0}
                self.annotationhistory['Name'] = np.append(self.annotationhistory['Name'], by.name)
                self.annotationhistory['ItWas'] = np.append(self.annotationhistory['ItWas'], as_being_dict[as_being])
                self.annotationhistory['At_X'].append(at_x)
                self.annotationhistory['At_Y'].append(at_y)
                self.annotationhistory['PL'] = np.append(self.annotationhistory['PL'], by.PL)
                self.annotationhistory['PD'] = np.append(self.annotationhistory['PD'], by.PD)
                self.annotationhistory['At_Time'].append(at_time)

        # Deal with active subjects. Ignore the classifier until they
        # have seen NT > a_few_at_the_start (ie they've had a
        # certain amount of training - at least one training image, for example):

            if by.NT > a_few_at_the_start:

                # Calculate likelihood for all Ntrajectory trajectories, generating as many binomial deviates
                if realize_confusion:

                    PL_realization=by.get_PL_realization(Ntrajectory);
                    PD_realization=by.get_PD_realization(Ntrajectory);
                else:
                    PL_realization=np.ones(Ntrajectory) * by.PL
                    PD_realization=np.ones(Ntrajectory) * by.PD
                prior_probability=self.probability*1.0;  # TODO: not used?!

                if as_being == 'LENS':
                    likelihood = PL_realization + laplace_smoothing
                    likelihood /= (PL_realization*self.probability + (1-PD_realization)*(1-self.probability) + 2 * laplace_smoothing)
                    as_being_number = 1

                elif as_being == 'NOT':
                    likelihood = (1-PL_realization) + laplace_smoothing
                    likelihood /= ((1-PL_realization)*self.probability + PD_realization*(1-self.probability) + 2 * laplace_smoothing)
                    as_being_number = 0

                else:
                    raise Exception("Unrecognised classification result: "+as_being)

                if online:
                    # Update subject:
                    self.probability = likelihood*self.probability
                    idx=np.where(self.probability < swap.pmin)
                    self.probability[idx]=swap.pmin
                    #if self.probability < swap.pmin: self.probability = swap.pmin
                    posterior_probability=self.probability*1.0;

                    self.trajectory = np.append(self.trajectory,self.probability)

                    self.exposure += 1

                    self.update_state(at_time)

                    # Update agent - training history is taken care of in agent.heard(),
                    # which also keeps agent.skill up to date.
                    if self.kind == 'test' and record:

                         by.testhistory['ID'] = np.append(by.testhistory['ID'], self.ID)
                         by.testhistory['I'] = np.append(by.testhistory['I'], swap.informationGain(self.mean_probability, by.PL, by.PD, as_being))
                         by.testhistory['Skill'] = np.append(by.testhistory['Skill'], by.skill)
                         by.testhistory['ItWas'] = np.append(by.testhistory['ItWas'], as_being_number)
                         by.testhistory['At_Time'] = np.append(by.testhistory['At_Time'], at_time)
                         by.contribution += by.skill

                else:
                    # offline
                    return likelihood


            else:
                # Still advance exposure, even if by.NT <= ignore:
                # it would be incorrect to calculate mean classns/retirement
                # different from strict and alt-strict:
                self.exposure += 1

        return

# ----------------------------------------------------------------------
# Update probability of LENS, given many classifications at once (E step):

    def was_described_many_times(self, bureau, names, classifications, record=False, haste=False, while_ignoring=-1,realize_confusion=False,laplace_smoothing=0):
        # classifications is assumed to be a list of 0s and 1s for NOT and LENS
        # names is assumed to just be a list of agent names
        N_classifications_used = 0
        likelihood_sum = 0

        if len(names) != len(classifications):
            raise Exception('len names {0} != len classifications {1}'.format(len(names), len(classifications)))
        for name, classification in zip(names, classifications):
            agent = bureau.member[name]
            if agent.kind == 'banned':
                continue

            by = agent
            as_being = ['NOT', 'LENS'][classification]
            likelihood_sum += self.was_described(by=by,as_being=as_being,while_ignoring=while_ignoring,haste=haste,online=False,record=record,realize_confusion=realize_confusion,laplace_smoothing=laplace_smoothing)
            N_classifications_used += 1
        self.probability = likelihood_sum * self.probability / N_classifications_used
        self.update_state()

        return

# ----------------------------------------------------------------------
# Update mean and median probability, status, retirement

    def update_state(self,at_time=None):
        # check if iterable
        try: iterator = iter(self.probability)
        except TypeError:
            self.mean_probability=self.probability
            self.median_probability=self.mean_probability
        else:
            # is iterable
            # Update median probability
            self.mean_probability=10.0 ** np.mean(np.log10(self.probability))
            self.median_probability=np.median(self.probability)

        # Should we count it as a detection, or a rejection?
        # Only test subjects get de-activated:

        if self.mean_probability < self.rejection_threshold:
            self.status = 'rejected'
            if self.kind == 'test':
                self.state = 'inactive'
                if at_time:
                    self.retirement_time = at_time
                else:
                    self.retirement_time = 'end of time'
                self.retirement_age = self.exposure

        elif self.mean_probability > self.detection_threshold:
            self.status = 'detected'
            if self.kind == 'test':
                # Let's keep the detections live!
                #   self.state = 'inactive'
                #   self.retirement_time = at_time
                #   self.retirement_age = self.exposure
                pass

        else:
            # Keep the subject alive! This code is only reached if
            # we are not being hasty.
            self.status = 'undecided'
            if self.kind == 'test':
                self.state = 'active'
                self.retirement_time = 'not yet'
                self.retirement_age = 0.0


# ----------------------------------------------------------------------
# Plot subject's trajectory, as an overlay on an existing plot:

    def plot_trajectory(self,axes,highlight=False):

        plt.sca(axes[0])
        N = np.linspace(0, len(self.trajectory)/Ntrajectory+1, len(self.trajectory)/Ntrajectory, endpoint=True);
        N[0] = 0.5
        mdn_trajectory=np.array([]);
        sigma_trajectory_m=np.array([]);
        sigma_trajectory_p=np.array([]);
        for i in range(len(N)):
	    sorted_arr=np.sort(self.trajectory[i*Ntrajectory:(i+1)*Ntrajectory])
            sigma_p=sorted_arr[int(0.84*Ntrajectory)]-sorted_arr[int(0.50*Ntrajectory)]
            sigma_m=sorted_arr[int(0.50*Ntrajectory)]-sorted_arr[int(0.16*Ntrajectory)]
            mdn_trajectory=np.append(mdn_trajectory,sorted_arr[int(0.50*Ntrajectory)]);
            sigma_trajectory_p=np.append(sigma_trajectory_p,sigma_p);
            sigma_trajectory_m=np.append(sigma_trajectory_m,sigma_m);

        if self.kind == 'sim':
            colour = 'blue'
            linewidth = 1.5
            alpha = 0.3
            size = 40
        elif self.kind == 'dud':
            colour = 'red'
            linewidth = 1.5
            alpha = 0.3
            size = 40
        elif self.kind == 'test':
            colour = 'black'
            linewidth = 1.0
            alpha = 0.1
            size = 20

        if self.status == 'undecided':
            facecolour = colour
        else:
            facecolour = 'white'

        if highlight:
            # Thicker, darker line:
            plt.plot(mdn_trajectory,N,color=colour,alpha=0.5,linewidth=2.0, linestyle="-")
            # Bigger point:
            size = 60
        else:
            # Thinner, fainter line:
            plt.plot(mdn_trajectory,N,color=colour,alpha=alpha,linewidth=linewidth, linestyle="-")

        NN = N[-1]
        if NN > swap.Ncmax: NN = swap.Ncmax
        if highlight:
            # Heavier symbol:
            plt.scatter(mdn_trajectory[-1], NN, s=size, edgecolors=colour, facecolors=colour, alpha=1.0);
            plt.plot([mdn_trajectory[-1]-sigma_trajectory_m[-1],mdn_trajectory[-1]+sigma_trajectory_p[-1]],[NN,NN],color=colour,alpha=0.5);
        else:
            # Fainter symbol:
            plt.scatter(mdn_trajectory[-1], NN, s=size, edgecolors=colour, facecolors=colour, alpha=1.0);
            plt.plot([mdn_trajectory[-1]-sigma_trajectory_m[-1],mdn_trajectory[-1]+sigma_trajectory_p[-1]],[NN,NN],color=colour,alpha=alpha);



        # if self.kind == 'sim': print self.trajectory[-1], N[-1]

        return
