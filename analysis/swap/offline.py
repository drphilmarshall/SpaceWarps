#============================================================================
"""
NAME
    offline.py

PURPOSE
    Methods for calculating probability of lens as well as the confusion matrix
    via expectation maximization.

COMMENTS
    Though I allow "pi" (the prior probability) to vary, I don't actually use
    it in the Estep.

    There is also considerable room to modify the EM algorithm (setting
    convergence criteria, etc.).

    Brief description of the inputs needed:
      bureau_offline : dictionary of bureau_offline from collection. Has
        properties Theta0, Theta1, PL, PD, Pi, and collection (a dictionary of
        all evaluations).
        I call it 'bureau' because it is a collection of agents, but '_offline'
        to distinguish it from the online bureaus, which have different keys.
      pi : Prior probability of being a lens
      collection : the collection of lenses used
      taus : Final probability of being a lens
      training_IDs : which entries in collection are training (have known truth
        value)?

EXAMPLE
      Here is an example to set up and run the EM algorithm:


        bureau_offline = {}
        pi = 2e-4
        taus = {}
        online_taus = {}
        training_IDs = {}  # which entries in collection are training
        training_IDs_blank = {}  # we don't train on training_IDs
        set_aside_subject = {}  # which subjects do we set aside? Here we set aside none
        set_aside_agent = {}  # which agents do we set aside? Here we set aside none
        n_min = 1  # minimum number of assessments required to be considered


        collection = {}
        for ID in collection1.list():
            if ID in set_aside_subject:
                continue
            else:
                collection.update({ID: collection1.member[ID]})
        # TODO: maybe repeat the same process for bureau?
        bureau = bureau1



        for ID in subjects.list():
            subject = subjects.member[ID]
            n_assessment = len(subject.annotationhistory['ItWas'])
            if (n_assessment > n_min):
                if (subject.category == 'training'):
                    truth = {'LENS': 1, 'NOT': 0}[subject.truth]
                    # NOTE: setting this aside for here.
                    training_IDs.update({ID: truth})
                taus.update({ID: pi})
                online_taus.update({ID: subject.mean_probability})
                for agent_i in xrange(len(subject.annotationhistory['Name'])):
                    name = subject.annotationhistory['Name'][agent_i]
                    if name in set_aside_agent:
                        continue
                    xij = subject.annotationhistory['ItWas'][agent_i]
                    if name not in bureau_offline:
                        bureau_offline.update({name: {'Theta0': 0.75, 'Theta1': 0.75,
                                              'PL': bureau.member[name].PL,
                                              'PD': bureau.member[name].PD,
                                              'Pi': pi,
                                              'Subjects': {ID: xij}}})
                    else:
                        bureau_offline[name]['Subjects'].update({ID: xij})

        # Run EM Algorithm

        bureau_offline, pi, subjects, taus, information_dict = EM_algorithm(
                bureau_offline, pi, subjects, taus, training_IDs_blank,
                return_information=True)

METHODS
    Estep(bureau_offline, pi, collection, taus, training_IDs={})
    Mstep(bureau_offline, pi, collection, taus, training_IDs={})
    EM_algorithm(bureau_offline, pi, collection, taus, training_IDs={},
                 return_information=False)

BUGS

AUTHORS
  The code in this file was written by Christopher Davis in May-July 2014 at
  SLAC National Laboratory.
  This file is part of the Space Warps project, which is distributed 
  under the GPL v2 by the Space Warps Science Team.
  http://spacewarps.org/

HISTORY
  2014-07-16  Made into separate file by Davis.

LICENCE
  The MIT License (MIT)

  Copyright (c) 2014 CitizenScienceInAstronomyWorkshop

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
"""
#============================================================================

from numpy import square, sqrt

# ----------------------------------------------------------------------------
# Expectation Step

def Estep_old(bureau_offline, pi, collection, taus, training_IDs={}):
    # evaluate taus given collection of collection and current evaluation of
    # bureau_offline
    taus_prime = taus.copy()
    for ID in taus:
        pi_ij = taus[ID] #pi
        tau_j = 0
        N_j = 0

        # # this part cannot be efficient!
        # for name in bureau_offline:
        #     agent = bureau_offline[name]

        #     if ID not in agent['Subjects']:
        #         continue

        subject = collection.member[ID]
        for agent_i in xrange(len(subject.annotationhistory['Name'])):
            name = subject.annotationhistory['Name'][agent_i]
            agent = bureau_offline[name]
            xij = agent['Subjects'][ID]
            thetai0 = agent['Theta0']
            thetai1 = agent['Theta1']

            # xij = 1 term
            pos = thetai1 ** xij * (1 - thetai1) ** (1 - xij) * pi_ij
            neg = thetai0 ** (1 - xij) * (1 - thetai0) ** xij * (1 - pi_ij)
            tau_j += pos * 1. / (pos + neg)

            # xij = 0 term
            N_j += 1
        tau_j = tau_j * 1. / N_j

        taus_prime.update({ID: tau_j})
    return taus_prime

def Estep(bureau_offline, pi, taus, training_IDs={}):
    # evaluate taus given collection of collection and current evaluation of
    # bureau_offline
    taus_prime = taus.copy()
    taus_calculation = {}
    taus_skip = []

    for name in bureau_offline:

        agent = bureau_offline[name]
        thetai0 = agent['Theta0']
        thetai1 = agent['Theta1']

        for ID in agent['Subjects']:
            if ID in taus_skip:
                # not sure why this would happen (maybe from setting aside
                # guys? I dunno) but I think this is a good idea
                continue

            xij = agent['Subjects'][ID]

            if ID not in taus_calculation:
                # [tau_j, N_j, pi_ij]
                try:
                    taus_calculation.update({ID: [0, 0, taus[ID]]})
                except KeyError:
                    taus_skip.append(ID)
                    continue
            tau_j = taus_calculation[ID][0]
            N_j = taus_calculation[ID][1]
            pi_ij = taus_calculation[ID][2]

            pos = thetai1 ** xij * (1 - thetai1) ** (1 - xij) * pi_ij
            neg = thetai0 ** (1 - xij) * (1 - thetai0) ** xij * (1 - pi_ij)
            tau_j += pos * 1. / (pos + neg)

            N_j += 1

            # update taus_calculation
            taus_calculation[ID] = [tau_j, N_j, pi_ij]

    # now do taus_calculation and put it into taus_prime
    for ID in taus_calculation:
        taus_prime.update({ID:
            taus_calculation[ID][0] * 1. / taus_calculation[ID][1]})
    return taus_prime

# ----------------------------------------------------------------------------
# Maximization step.

def Mstep(bureau_offline, pi, taus, training_IDs={}):
    pi_num = 0
    pi_den = 0
    bureau_offline_prime = bureau_offline.copy()
    for name in bureau_offline:
        agent = bureau_offline[name]
        agent_prime = agent.copy()  # so that it has PL, PD, Subjects
        thetai1_num = 0
        thetai1_den = 0
        thetai0_num = 0
        thetai0_den = 0
        # pii_num = thetai1_den
        pii_den = 0
        for ID in agent['Subjects']:
            if ID in taus:

                # Incorporate true value of training values
                if ID in training_IDs:
                    tauj = training_IDs[ID]
                else:
                    tauj = taus[ID]

                xij = agent['Subjects'][ID]

                thetai0_num += (1 - xij) * (1 - tauj)
                thetai0_den += 1 - tauj
                thetai1_num += xij * tauj
                thetai1_den += tauj
                pii_den += 1
        # I think this is OK?
        if thetai0_den == 0:
            thetai0_den = 1
        if thetai1_den == 0:
            thetai1_den = 1

        agent_prime.update({'Theta0': thetai0_num * 1. / thetai0_den,
                            'Theta1': thetai1_num * 1. / thetai1_den,
                            'Pi': thetai1_den * 1. / pii_den,})
        bureau_offline_prime.update({name: agent_prime})
        pi_num += thetai1_den
        pi_den += pii_den
    pi = pi_num * 1. / pi_den
    return bureau_offline_prime, pi

# ----------------------------------------------------------------------------
# Expectation Maximization algorithm.

def EM_algorithm(bureau_offline, pi, taus, training_IDs={},
                 return_information=False):
    epsilon_taus = 10
    N_max = 50
    N_min = 10
    N_try = 0
    epsilon_min = 1e-5
    epsilon_list = []

    while (epsilon_taus > epsilon_min) * (N_try < N_max) + (N_try < N_min):

        # E step
        # for each tau_j go through all classifications i done on j: x_ij
        taus_prime = Estep(bureau_offline, pi, taus, training_IDs)
        # evaluate change in probability
        epsilon_taus = 0
        for ID in taus:
            epsilon_taus += square(taus[ID] - taus_prime[ID])
        taus = taus_prime

        # M step
        bureau_offline_prime, pi_prime = Mstep(
                bureau_offline, pi, taus, training_IDs)
        bureau_offline = bureau_offline_prime
        pi = pi_prime

        # divide epsilon_taus by the number of taus
        epsilon_taus = sqrt(epsilon_taus) * 1. / len(taus.keys())
        epsilon_list.append(epsilon_taus)
        N_try += 1

    if return_information:
        information_dict = {'N_try': N_try,
                            'epsilon_list': epsilon_list,
                            'epsilon_taus': epsilon_taus,
                            'epsilon_min': epsilon_min,
                            'N_max': N_max,
                            'N_min': N_min}
        return bureau_offline, pi, taus, information_dict
    else:
        return bureau_offline, pi, taus

#============================================================================
