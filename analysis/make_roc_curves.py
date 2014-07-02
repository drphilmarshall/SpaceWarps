#!/usr/bin/env python
# ======================================================================

import sys,getopt,numpy as np
from sklearn.metrics import roc_curve

import matplotlib
# Force matplotlib to not use any Xwindows backend:
matplotlib.use('Agg')

# Fonts, latex:
matplotlib.rc('font',**{'family':'serif', 'serif':['TimesNewRoman']})
matplotlib.rc('text', usetex=True)

from matplotlib import pyplot as plt

bfs,sfs = 20,16
params = { 'axes.labelsize': bfs,
            'text.fontsize': bfs,
          'legend.fontsize': bfs,
          'xtick.labelsize': sfs,
          'ytick.labelsize': sfs}
plt.rcParams.update(params)

import swap

# ======================================================================

def make_roc_curves(argv):
    """
    NAME
        make_roc_curves

    PURPOSE
        Given the stage1 and stage2 bureau and collection pickles, this script
        produces the one roc plot that will be put someplace in the SW system
        paper. You can also do an Expectation Maximization for offline
        processing.

    COMMENTS
        For the offline assessments, see em.pdf in the docs directory.

    FLAGS
        -h                Print this message
        -o                Do the offline EM processing

    INPUTS
        --offline 0/1
        stage1_bureau.pickle
        stage2_bureau.pickle
        stage1_collection.pickle
        stage2_collection.pickle

    OUTPUTS
        an roc png plot

    EXAMPLE

    BUGS
        - Code is not tested yet...

    AUTHORS
        This file is part of the Space Warps project, and is distributed
        under the GPL v2 by the Space Warps Science Team.
        http://spacewarps.org/

    HISTORY
      2013-07-01  started Davis (KIPAC)
    """

    # ------------------------------------------------------------------

    try:
       opts, args = getopt.getopt(argv,"ho",["help","offline"])
    except getopt.GetoptError, err:
       print str(err) # will print something like "option -a not recognized"
       print make_roc_curves.__doc__  # will print the big comment above.
       return

    offline = 0
    resurrect = False

    for o,a in opts:
       if o in ("-h", "--help"):
          print make_roc_curves.__doc__
          return
       elif o in ("-o", "--offline"):
          offline = int(a)
       else:
          assert False, "unhandled option"

    # Check for pickles in array args:
    if len(args) == 4:
        bureau1_path = args[0]
        bureau2_path = args[1]
        collection1_path = args[2]
        collection2_path = args[3]
        print "make_roc_curves: illustrating behaviour captured in bureau and collection files: "
        print "make_roc_curves: ",bureau1_path
        print "make_roc_curves: ",bureau2_path
        print "make_roc_curves: ",collection1_path
        print "make_roc_curves: ",collection2_path
    else:
        print make_roc_curves.__doc__
        return

    output_directory = './'

    # ------------------------------------------------------------------

    # Read in bureau and collection objects:
    bureau1 = swap.read_pickle(bureau1_path, 'bureau')
    collection1 = swap.read_pickle(collection1_path, 'collection')
    bureau2 = swap.read_pickle(bureau2_path, 'bureau')
    collection2 = swap.read_pickle(collection2_path, 'collection')

    print "make_roc_curves: stage 1, 2 agent numbers: ",len(bureau1.list()), len(bureau2.list())

    print "make_roc_curves: stage 1, 2 subject numbers: ",len(collection1.list()), len(collection2.list())


    # ------------------------------------------------------------------
    # if we do the EM offline processing for stage2:
    # NOTE: it is not inconceivable to also do this for stage1...
    if offline:
        print "make_roc_curves: doing offline processing!"

        # NOTE: pi is currently NOT USED
        def Estep(taus, agents, subjects, pi, set_aside={}):
            # evaluate taus given collection of subjects and current evaluation of agents
            taus_prime = taus.copy()
            for ID in taus:
                if ID in set_aside:
                    continue
                pi_ij = taus[ID] #pi
                subject = subjects.member[ID]
                tau_j = 0
                N_j = 0
                for agent_i in xrange(len(subject.annotationhistory['Name'])):
                    name = subject.annotationhistory['Name'][agent_i]
                    agent = agents[name]
                    xij = agent['Subjects'][ID]
                    thetai0 = agent['Theta0']
                    thetai1 = agent['Theta1']

                    # xij = 1 term
                    pos = thetai1 ** xij * (1 - thetai1) ** (1 - xij) * pi_ij
                    neg = thetai0 ** (1 - xij) * (1 - thetai0) ** xij * (1 - pi_ij)
                    tau_j += pos / (pos + neg)

                    # xij = 0 term
                    N_j += 1
                tau_j /= N_j

                taus_prime.update({ID: tau_j})
            return taus_prime

        def Mstep(agents, taus, pi, training_IDs={}, set_aside={}):
            pi_num = 0
            pi_den = 0
            agents_prime = agents.copy()
            for name in agents:
                agent = agents[name]
                agent_prime = agent.copy()
                thetai1_num = 0
                thetai1_den = 0
                thetai0_num = 0
                thetai0_den = 0
                # pii_num = thetai1_den
                pii_den = 0
                for ID in agent['Subjects']:
                    if ID in set_aside:
                        continue
                    if ID in taus:
                        tauj = taus[ID]

                        # Incorporate true value of training values
                        if ID in training_IDs:
                            tauj = training_IDs[ID]
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

                agent_prime.update({'Theta0': thetai0_num / thetai0_den,
                                    'Theta1': thetai1_num / thetai1_den,
                                    'Pi': thetai1_den / pii_den,})
                agents_prime.update({name: agent_prime})
                pi_num += thetai1_den
                pi_den += pii_den
            pi = pi_num / pi_den
            return agents_prime, pi


        # Set up data for EM algorithm

        agents = {}
        taus = {}
        online_taus = {}
        training_IDs = {}  # which entries in collection are training
        set_aside = {}  # which entries do we set aside? Here we set aside none
        n_min = 1  # minimum number of assessments required to be considered


        collection = collection2
        bureau = bureau2

        for ID in collection.list():
            subject = collection.member[ID]
            n_assessment = len(subject.annotationhistory['ItWas'])
            if (n_assessment > n_min):
                if (subject.category == 'training'):
                    truth = {'LENS': 1, 'NOT': 0}[subject.truth]
                    training_IDs.update({ID: truth})
                taus.update({ID: pi})
                online_taus.update({ID: subject.mean_probability})
                for agent_i in xrange(len(subject.annotationhistory['Name'])):
                    name = subject.annotationhistory['Name'][agent_i]
                    xij = subject.annotationhistory['ItWas'][agent_i]
                    if name not in agents:
                        agents.update({name: {'Theta0': 0.75, 'Theta1': 0.75,
                                              'PL': bureau.member[name].PL,
                                              'PD': bureau.member[name].PD,
                                              'Pi': pi,
                                              'Subjects': {ID: xij}}})
                    else:
                        agents[name]['Subjects'].update({ID: xij})


        # Run EM Algorithm

        epsilon_taus = 10
        N_max = 50
        N_min = 10
        N_try = 0
        epsilon_min = 1e-5
        epsilon_list = []

        while (epsilon_taus > epsilon_min) * (N_try < N_max) + (N_try < N_min):

            # E step
            # for each tau_j go through all classifications i done on j: x_ij
            taus_prime = Estep(taus, agents, collection, pi, set_aside)
            # evaluate change in probability
            epsilon_taus = 0
            for ID in taus:
                epsilon_taus += np.square(taus[ID] - taus_prime[ID])
            taus = taus_prime

            # M step
            agents_prime, pi_prime = Mstep(agents, taus, pi, training_IDs, set_aside)
            agents = agents_prime
            pi = pi_prime

            # divide epsilon_taus by the number of taus
            epsilon_taus = np.sqrt(epsilon_taus) / len(taus.keys())
            epsilon_list.append(epsilon_taus)
            N_try += 1

        print "make_roc_curves: offline processing done! epsilon, number of iterations", epsilon_taus, N_try

    # ------------------------------------------------------------------
    # set up data for roc plots

    n_min = 1

    fprs = []
    tprs = []
    thresholds = []
    collections = [collection_1, collection_2]

    # create the online fpr and tpr
    for collection in collections:
        y_true = np.array([])
        y_score = np.array([])
        for ID in collection.list():
            subject = collection.member[ID]
            if (subject.category == 'training'):
            n_assessment = len(subject.annotationhistory['ItWas'])
                if (n_assessment > n_min):
                        truth = {'LENS': 1, 'NOT': 0}[subject.truth]
                        y_true = np.append(y_true, truth)
                        y_score = np.append(y_score, subject.mean_probability)

        fpr, tpr, threshold = roc_curve(y_true, y_score)
        fprs.append(fpr)
        tprs.append(tpr)
        thresholds.append(threshold)

    # now do the stage 2 offline if we wish
    if offline:
        y_true = np.array([])
        y_score = np.array([])
        for ID in training_IDs:
            # sometimes I get nans?!
            if taus[ID] == taus[ID]:
                subject = collection.member[ID]
                truth = {'LENS': 1, 'NOT': 0}[subject.truth]
                y_true = np.append(y_true, truth)
                y_score = np.append(y_score, taus[ID])
        fpr, tpr, threshold = roc_curve(y_true, y_score)
        fprs.append(fpr)
        tprs.append(tpr)
        thresholds.append(threshold)

    # ------------------------------------------------------------------
    # do roc curves

    fig, ax = plt.subplots(figsize=(10,8))
    ax.plot(fprs[0], tprs[0], 'b', label='stage 1 online', linewidth=3)
    ax.plot(fprs[1], tprs[1], 'DarkOrange', label='stage 2 online', linewidth=3)
    if offline:
        ax.plot(fprs[2], tprs[2], 'DarkOrange', linestyle='--', label='stage 2 offline', linewidth=3)

    ax.set_xlim(0, 0.1)
    ax.set_ylim(0.8, 1)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    plt.legend(loc='lower right')

    pngfile = output_directory + 'roc_curve.png'
    plt.savefig(pngfile)


    print "make_roc_curves: roc curve saved to "+pngfile

    # ------------------------------------------------------------------

    print "make_roc_curves: all done!"

    return

# ======================================================================

if __name__ == '__main__':
    make_roc_curves(sys.argv[1:])

# ======================================================================
