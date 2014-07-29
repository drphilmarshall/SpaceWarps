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
from swap.offline import EM_algorithm

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
        -h                          Print this message
        --offline_stage1    0/1     Do offline analysis for stage1
        --offline_stage2    0/1     Do offline analysis for stage2
        --save_offline      0/1     Save the results of offline analysis?

    INPUTS
        stage1_bureau.pickle
        stage2_bureau.pickle
        stage1_collection.pickle
        stage2_collection.pickle

    OUTPUTS
        roc png plot

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
        opts, args = getopt.getopt(argv,"h",
                ["help", "offline_stage1", "offline_stage2", "offline_save",
                 "offline_no_training"])
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        print make_roc_curves.__doc__  # will print the big comment above.
        return

    offline_stage1 = 0
    offline_stage2 = 0
    use_training_info = 1
    save_offline = 0

    for o,a in opts:
        print o,a
        if o in ("-h", "--help"):
            print make_roc_curves.__doc__
            return
        elif o in ("--offline_stage1"):
            offline_stage1 = 1
        elif o in ("--offline_stage2"):
            offline_stage2 = 1
        elif o in ("--offline_save"):
            save_offline = 1
        elif o in ("--offline_no_training"):
            use_training_info = 0
        else:
            assert False, "unhandled option"
    print "make_roc_curves: offline is",offline_stage1, offline_stage2

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
    # set up data for roc plots

    n_min = 1

    fprs = []
    tprs = []
    thresholds = []
    collections = [collection1, collection2]

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

    # ------------------------------------------------------------------
    # if we do the EM offline processing for stage1:
    if offline_stage1:
        print "make_roc_curves: doing offline_stage1 processing!"

        # Set up data for EM algorithm

        bureau_offline = {}
        pi = 4e-2
        taus = {}
        online_taus = {}
        training_IDs = {}  # which entries in collection are training
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

        for ID in collection.keys():
            subject = collection[ID]
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
                        bureau_offline.update({name: {
                            'Theta0': 0.75, 'Theta1': 0.75,
                            'PL': bureau.member[name].PL,
                            'PD': bureau.member[name].PD,
                            'Pi': pi,
                            'Subjects': {ID: xij}}})
                    else:
                        bureau_offline[name]['Subjects'].update({ID: xij})

        # Run EM Algorithm

        if not use_training_info:
            bureau_offline, pi, taus, information_dict = EM_algorithm(
                    bureau_offline, pi, taus, {},
                    return_information=True)

        else:
            bureau_offline, pi, taus, information_dict = EM_algorithm(
                    bureau_offline, pi, taus, training_IDs,
                    return_information=True)

        if save_offline:
            tup = (bureau_offline, pi, taus, information_dict)
            offlinefile = output_directory + 'offline_stage1.pickle'
            swap.io.write_pickle(tup, offlinefile)
            print "make_roc_curves: offline_stage1 saved to ", offlinefile

        epsilon_taus = information_dict['epsilon_taus']
        N_try = information_dict['N_try']

        print "make_roc_curves: offline_stage1 processing done! epsilon, number of iterations", epsilon_taus, N_try

        y_true = np.array([])
        y_score = np.array([])
        for ID in training_IDs:
            # sometimes I get nans?!
            if taus[ID] == taus[ID]:
                subject = collection[ID]
                truth = {'LENS': 1, 'NOT': 0}[subject.truth]
                y_true = np.append(y_true, truth)
                y_score = np.append(y_score, taus[ID])
        fpr_offline_stage1, tpr_offline_stage1, threshold_offline_stage1 = roc_curve(y_true, y_score)

    # ------------------------------------------------------------------
    # if we do the EM offline processing for stage2:
    if offline_stage2:
        print "make_roc_curves: doing offline_stage2 processing!"

        # Set up data for EM algorithm

        bureau_offline = {}
        pi = 4e-2
        taus = {}
        online_taus = {}
        training_IDs = {}  # which entries in collection are training
        set_aside_subject = {}  # which subjects do we set aside? Here we set aside none
        set_aside_agent = {}  # which agents do we set aside? Here we set aside none
        n_min = 1  # minimum number of assessments required to be considered

        collection = {}
        for ID in collection2.list():
            if ID in set_aside_subject:
                continue
            else:
                collection.update({ID: collection2.member[ID]})
        # TODO: maybe repeat the same process for bureau?
        bureau = bureau2


        for ID in collection.keys():
            subject = collection[ID]
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
                        bureau_offline.update({name: {
                            'Theta0': 0.75, 'Theta1': 0.75,
                            'PL': bureau.member[name].PL,
                            'PD': bureau.member[name].PD,
                            'Pi': pi,
                            'Subjects': {ID: xij}}})
                    else:
                        bureau_offline[name]['Subjects'].update({ID: xij})


        # Run EM Algorithm

        if not use_training_info:
            bureau_offline, pi, taus, information_dict = EM_algorithm(
                    bureau_offline, pi, taus, {},
                    return_information=True)

        else:
            bureau_offline, pi, taus, information_dict = EM_algorithm(
                    bureau_offline, pi, taus, training_IDs,
                    return_information=True)

        if save_offline:
            tup = (bureau_offline, pi, taus, information_dict)
            offlinefile = output_directory + 'offline_stage2.pickle'
            swap.io.write_pickle(tup, offlinefile)
            print "make_roc_curves: offline_stage1 saved to ", offlinefile


        epsilon_taus = information_dict['epsilon_taus']
        N_try = information_dict['N_try']

        print "make_roc_curves: offline_stage2 processing done! epsilon, number of iterations", epsilon_taus, N_try

        y_true = np.array([])
        y_score = np.array([])
        for ID in training_IDs:
            # sometimes I get nans?!
            if taus[ID] == taus[ID]:
                subject = collection[ID]
                truth = {'LENS': 1, 'NOT': 0}[subject.truth]
                y_true = np.append(y_true, truth)
                y_score = np.append(y_score, taus[ID])
        fpr_offline_stage2, tpr_offline_stage2, threshold_offline_stage2 = roc_curve(y_true, y_score)

    # ------------------------------------------------------------------
    # do roc curves

    fig, ax = plt.subplots(figsize=(10,8))
    ax.plot(fprs[0], tprs[0], 'b', label='stage 1', linewidth=3)
    ax.plot(fprs[1], tprs[1], 'DarkOrange', label='stage 2', linewidth=3)
    if offline_stage1:
        ax.plot(fpr_offline_stage1, tpr_offline_stage1, 'b', linestyle='--', label='stage 1 offline', linewidth=3)
    if offline_stage2:
        ax.plot(fpr_offline_stage2, tpr_offline_stage2, 'DarkOrange', linestyle='--', label='stage 2 offline', linewidth=3)

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
