#!/usr/bin/env python
# ======================================================================

import sys, getopt, numpy as np

import matplotlib
# Force matplotlib to not use any Xwindows backend:
matplotlib.use('Agg')

# Fonts, latex:
matplotlib.rc('font', **{'family':'serif', 'serif':['TimesNewRoman']})
matplotlib.rc('text', usetex=True)

from matplotlib import pyplot as plt

bfs, sfs = 20, 16
params = { 'axes.labelsize': bfs,
            'text.fontsize': bfs,
          'legend.fontsize': bfs,
          'xtick.labelsize': sfs,
          'ytick.labelsize': sfs}
plt.rcParams.update(params)

origin = 'lower'

import swap

from swap.offline import EM_algorithm

# ======================================================================

def make_offline_reports(args):
    """
    NAME
        make_offline_reports

    PURPOSE
        Given an offline tuple as well as other bureau tuples etc,
        this script produces the reports made at the end of SWAP

    COMMENTS

    FLAGS
        -h              Print this message
        --out           Output directory, otherwise is '.'
        --do_offline    Do offline analysis?

    INPUTS
        configfile Plain text file containing SW experiment configuration
        bureaufile
        collectionfile


    OUTPUTS

    EXAMPLE

    BUGS

    AUTHORS
        This file is part of the Space Warps project, and is distributed
        under the GPL v2 by the Space Warps Science Team.
        http://spacewarps.org/

    HISTORY
        2014-09-16  started Davis (KIPAC)
    """
    # ------------------------------------------------------------------
    # Some defaults:

    # default settings are for offline using only exact training info
    flags = {'do_offline': False,
             'output_directory': '.',
             'PL0': 0.5,  # initial PL guess
             'PD0': 0.5,  # initial PD guess
             'pi': 4e-2,  # initial lens probability
             'n_min_assessment': 0,  # minimum number of assessments before included in analysis
             'use_training_info': True,
             'exclude_test_info': True,
             'exclude_training_info': False,
             'N_min': 10,  # min number of EM steps required
             'N_max': 100,  # max number of EM steps
             'epsilon_min': 1e-6,  # escape condition
             }

    # this has to be easier to do...
    for arg in args:
        if arg in flags:
            flags[arg] = args[arg]
        elif arg == 'config':
            configfile = args[arg]
        elif arg == 'collection':
            collectionfile = args[arg]
        elif arg == 'bureau':
            bureaufile = args[arg]
        else:
            print "make_offline_reports: unrecognized flag ",arg

    out_dir = flags['output_directory']

    # ------------------------------------------------------------------
    # Read in run configuration:
    tonights = swap.Configuration(configfile)
    # TODO: do this correctly
    tonights.parameters['finish'] = 'now'
    tonights.parameters['start'] = 'now'
    tonights.parameters['trunk'] = \
        tonights.parameters['survey']+'_'+tonights.parameters['finish']
    tonights.parameters['dir'] = out_dir
    # How will we make decisions based on probability?
    thresholds = {}
    thresholds['detection'] = tonights.parameters['detection_threshold']
    thresholds['rejection'] = tonights.parameters['rejection_threshold']

    t = -1  # for now?!

    # ------------------------------------------------------------------
    # Read in, or create, a bureau of agents who will represent the
    # volunteers:

    bureau = swap.read_pickle(bureaufile, 'bureau')

    # ------------------------------------------------------------------
    # Read in, or create, an object representing the candidate list:

    sample = swap.read_pickle(collectionfile, 'collection')


    # ------------------------------------------------------------------
    # if do_offline, run offline analysis here:

    if flags['do_offline']:
        PL0 = flags['PL0']
        PD0 = flags['PD0']
        pi = flags['pi']
        n_min_assessment = flags['n_min_assessment']
        use_training_info = flags['use_training_info']
        exclude_test_info = flags['exclude_test_info']
        exclude_training_info = flags['exclude_training_info']
        N_min = flags['N_min']
        N_max = flags['N_max']
        epsilon_min = flags['epsilon_min']

        # initialize offline params
        bureau_offline = {}
        probabilities = {}
        online_probabilities = {}
        training_IDs = {}  # which entries in collection are training
        set_aside_subject = {}  # which subjects do we set aside? Here we set aside none
        set_aside_agent = {}  # which agents do we set aside? Here we set aside none

        collection = {}
        for ID in sample.list():
            if ID in set_aside_subject:
                continue
            else:
                collection.update({ID: sample.member[ID]})

        for ID in collection.keys():
            subject = collection[ID]
            n_assessment = len(subject.annotationhistory['ItWas'])
            if (n_assessment > n_min_assessment):
                if (subject.category == 'training'):
                    if use_training_info:
                        truth = {'LENS': 1, 'NOT': 0}[subject.truth]
                        training_IDs.update({ID: truth})
                    if exclude_training_info:
                        # when doing M step, don't use these to update parameters
                        training_IDs.update({ID: -1})
                elif (subject.category == 'test'):
                    if exclude_test_info:
                        # when doing M step, don't use these to update parameters
                        training_IDs.update({ID: -1})
                probabilities.update({ID: pi})
                online_probabilities.update({ID: subject.mean_probability})
                for agent_i in xrange(len(subject.annotationhistory['Name'])):
                    name = subject.annotationhistory['Name'][agent_i]
                    if name in set_aside_agent:
                        continue
                    xij = subject.annotationhistory['ItWas'][agent_i]
                    if name not in bureau_offline:
                        bureau_offline.update({name: {
                            'PD': PD0, 'PL': PL0,
                            'PL_in': bureau.member[name].PL,
                            'PD_in': bureau.member[name].PD,
                            'Pi': pi,
                            'Subjects': {ID: xij}}})
                    else:
                        bureau_offline[name]['Subjects'].update({ID: xij})

        # Run EM Algorithm

        bureau_offline, pi, probabilities, information_dict = EM_algorithm(
                bureau_offline, pi, probabilities, training_IDs,
                N_min=N_min, N_max=N_max, epsilon_min=epsilon_min,
                return_information=True)

        tup = (bureau_offline, pi, probabilities, information_dict)
        offlinefile = out_dir + '/offline.pickle'
        swap.write_pickle(tup, offlinefile)

        # ------------------------------------------------------------------
        # Now replace sample member probabilities with offline probabilities
        # Also update bureau with offline results
        for ID in sample.list():
            # just in case any IDs didn't get into offline somehow?!
            if ID not in probabilities.keys():
                sample.member.pop(ID)
                continue
            # This is a bit hackish: update mean_probability,
            # median_probability, and do the rejection threshold stuff
            subject = sample.member[ID]
            subject.mean_probability = probabilities[ID]
            subject.median_probability = probabilities[ID]
            # ripped from subject.py
            if subject.mean_probability < subject.rejection_threshold:
                subject.status = 'rejected'
                if subject.kind == 'test':
                    subject.state = 'inactive'
                    subject.retirement_time = -1#at_time
                    subject.retirement_age = subject.exposure

            elif subject.mean_probability > subject.detection_threshold:
                subject.status = 'detected'
                if subject.kind == 'test':
                    # Let's keep the detections live!
                    #   subject.state = 'inactive'
                    #   subject.retirement_time = at_time
                    #   subject.retirement_age = subject.exposure
                    pass

            else:
                # Keep the subject alive! This code is only reached if
                # we are not being hasty.
                subject.status = 'undecided'
                if subject.kind == 'test':
                    subject.state = 'active'
                    subject.retirement_time = 'not yet'
                    subject.retirement_age = 0.0

            # I don't think this is necessary, but just in case
            sample.member[ID] = subject

        for kind in ['sim', 'dud', 'test']:
            sample.collect_probabilities(kind)

        # now save
        collectionfile = out_dir + '/collection_offline.pickle'
        swap.write_pickle(collection, collectionfile)

        # now update bureau
        for ID in bureau.list():
            # just in case any IDs didn't make it to offline?
            if ID not in bureau_offline.keys():
                bureau.member.pop(ID)
                continue
            # update PL, PD, then update_skill
            agent = bureau.member[ID]
            agent.PL = bureau_offline[ID]['PL']
            agent.PD = bureau_offline[ID]['PD']
            agent.update_skill()

            # I don't think this is necessary, but just in case
            bureau.member[ID] = agent

        bureau.collect_probabilities()


        # now save
        bureaufile = out_dir + '/bureau_offline.pickle'
        swap.write_pickle(bureau, bureaufile)

    # ------------------------------------------------------------------
    # now we can pretend we're in SWAP.py

    new_retirementfile = swap.get_new_filename(tonights.parameters,'retire_these')
    print "make_offline_reports: saving retiree subject Zooniverse IDs..."
    N = swap.write_list(sample,new_retirementfile,item='retired_subject')
    print "make_offline_reports: "+str(N)+" lines written to "+new_retirementfile

    # Also print out lists of detections etc! These are urls of images.

    new_samplefile = swap.get_new_filename(tonights.parameters,'candidates')
    print "make_offline_reports: saving lens candidates..."
    N = swap.write_list(sample,new_samplefile,item='candidate')
    print "make_offline_reports: "+str(N)+" lines written to "+new_samplefile

    # Now save the training images, for inspection:
    new_samplefile = swap.get_new_filename(tonights.parameters,'training_true_positives')
    print "make_offline_reports: saving true positives..."
    N = swap.write_list(sample,new_samplefile,item='true_positive')
    print "make_offline_reports: "+str(N)+" lines written to "+new_samplefile

    new_samplefile = swap.get_new_filename(tonights.parameters,'training_false_positives')
    print "make_offline_reports: saving false positives..."
    N = swap.write_list(sample,new_samplefile,item='false_positive')
    print "make_offline_reports: "+str(N)+" lines written to "+new_samplefile

    new_samplefile = swap.get_new_filename(tonights.parameters,'training_false_negatives')
    print "make_offline_reports: saving false negatives..."
    N = swap.write_list(sample,new_samplefile,item='false_negative')
    print "make_offline_reports: "+str(N)+" lines written to "+new_samplefile

    # Also write out catalogs of subjects, including the ZooID, subject ID,
    # how many classifications, and probability:

    catalog = swap.get_new_filename(tonights.parameters,'candidate_catalog')
    print "make_offline_reports: saving catalog of high probability subjects..."
    Nlenses,Nsubjects = swap.write_catalog(sample,catalog,thresholds,kind='test')
    print "make_offline_reports: From "+str(Nsubjects)+" subjects classified,"
    print "make_offline_reports: "+str(Nlenses)+" candidates (with P > rejection) written to "+catalog

    catalog = swap.get_new_filename(tonights.parameters,'sim_catalog')
    print "make_offline_reports: saving catalog of high probability subjects..."
    Nsims,Nsubjects = swap.write_catalog(sample,catalog,thresholds,kind='sim')
    print "make_offline_reports: From "+str(Nsubjects)+" subjects classified,"
    print "make_offline_reports: "+str(Nsims)+" sim 'candidates' (with P > rejection) written to "+catalog

    catalog = swap.get_new_filename(tonights.parameters,'dud_catalog')
    print "make_offline_reports: saving catalog of high probability subjects..."
    Nduds,Nsubjects = swap.write_catalog(sample,catalog,thresholds,kind='dud')
    print "make_offline_reports: From "+str(Nsubjects)+" subjects classified,"
    print "make_offline_reports: "+str(Nduds)+" dud 'candidates' (with P > rejection) written to "+catalog

    # ------------------------------------------------------------------

    # Make plots! Can't plot everything - uniformly sample 200 of each
    # thing (agent or subject).

    # Agent histories:

    fig1 = bureau.start_history_plot()
    pngfile = swap.get_new_filename(tonights.parameters,'histories')
    Nc = np.min([200,bureau.size()])
    print "make_offline_reports: plotting "+str(Nc)+" agent histories in "+pngfile

    for Name in bureau.shortlist(Nc):
        bureau.member[Name].plot_history(fig1)

    bureau.finish_history_plot(fig1,t,pngfile)
    tonights.parameters['historiesplot'] = pngfile

    # Agent probabilities:

    pngfile = swap.get_new_filename(tonights.parameters,'probabilities')
    print "make_offline_reports: plotting "+str(Nc)+" agent probabilities in "+pngfile
    bureau.plot_probabilities(Nc,t,pngfile)
    tonights.parameters['probabilitiesplot'] = pngfile

    # Subject trajectories:

    fig3 = sample.start_trajectory_plot()
    pngfile = swap.get_new_filename(tonights.parameters,'trajectories')

    # Random 500  for display purposes:
    Ns = np.min([500,sample.size()])
    print "make_offline_reports: plotting "+str(Ns)+" subject trajectories in "+pngfile

    for ID in sample.shortlist(Ns):
        sample.member[ID].plot_trajectory(fig3)

    # To plot only false negatives, or only true positives:
    # for ID in sample.shortlist(Ns,kind='sim',status='rejected'):
    #     sample.member[ID].plot_trajectory(fig3)
    # for ID in sample.shortlist(Ns,kind='sim',status='detected'):
    #     sample.member[ID].plot_trajectory(fig3)

    sample.finish_trajectory_plot(fig3,pngfile,t=t)
    tonights.parameters['trajectoriesplot'] = pngfile

    # Candidates! Plot all undecideds or detections:

    fig4 = sample.start_trajectory_plot(final=True)
    pngfile = swap.get_new_filename(tonights.parameters,'sample')

    # BigN = 100000 # Would get them all...
    BigN = 500      # Can't see them all!
    candidates = []
    candidates += sample.shortlist(BigN,kind='test',status='detected')
    candidates += sample.shortlist(BigN,kind='test',status='undecided')
    sims = []
    sims += sample.shortlist(BigN,kind='sim',status='detected')
    sims += sample.shortlist(BigN,kind='sim',status='undecided')
    duds = []
    duds += sample.shortlist(BigN,kind='dud',status='detected')
    duds += sample.shortlist(BigN,kind='dud',status='undecided')

    print "make_offline_reports: plotting "+str(len(sims))+" sims in "+pngfile
    for ID in sims:
        sample.member[ID].plot_trajectory(fig4)
    print "make_offline_reports: plotting "+str(len(duds))+" duds in "+pngfile
    for ID in duds:
        sample.member[ID].plot_trajectory(fig4)
    print "make_offline_reports: plotting "+str(len(candidates))+" candidates in "+pngfile
    for ID in candidates:
        sample.member[ID].plot_trajectory(fig4)

    # They will all show up in the histogram though:
    sample.finish_trajectory_plot(fig4,pngfile,final=True)
    tonights.parameters['candidatesplot'] = pngfile

    # ------------------------------------------------------------------
    # Finally, write a PDF report:

    swap.write_report(tonights.parameters,bureau,sample)



# ======================================================================

if __name__ == '__main__':
    # do argparse style; I find this /much/ easier than getopt (sorry Phil!)
    import argparse
    parser = argparse.ArgumentParser(description=make_offline_reports.__doc__)
    # Options we can configure
    parser.add_argument("--output_directory",
                        action="store",
                        dest="output_directory",
                        default=".",
                        help="Output directory for reports.")
    parser.add_argument("--do_offline",
                        action="store_true",
                        dest="do_offline",
                        default=False,
                        help="Do offline analysis if not already done.")
    parser.add_argument("--config",
                        dest="config",
                        help="Location of configfile.")
    parser.add_argument("--collection",
                        dest="collection",
                        help="Location of collectionfile.")
    parser.add_argument("--bureau",
                        dest="bureau",
                        help="Location of bureaufile.")

    options = parser.parse_args()
    args = vars(options)
    import sys
    argv_str = ''
    for argvi in sys.argv:
        argv_str += argvi + ' '
    print(argv_str)
    make_offline_reports(args)

# ======================================================================
