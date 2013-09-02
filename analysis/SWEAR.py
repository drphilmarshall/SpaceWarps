#!/usr/bin/env python
# ======================================================================

import swap

import sys,getopt,datetime,os,subprocess
import numpy as np

# ======================================================================

def SWEAR(argv):
    """
    NAME
        SWEAR.py

    PURPOSE
        
        Read in the SWAP output database pickles and produce plots and a
        report. 

    COMMENTS
        
    FLAGS
        -h            Print this message

    INPUTS
        configfile    Plain text file containing SW experiment configuration

    OUTPUTS
        stdout
        png figures, pdf report

    EXAMPLE
        
        cd workspace
        SWEAR.py update.config

    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-09-02  started. Marshall (KIPAC)
    """

    # ------------------------------------------------------------------

    try:
       opts, args = getopt.getopt(argv,"h",["help"])
    except getopt.GetoptError, err:
       print str(err) # will print something like "option -a not recognized"
       print SWEAR.__doc__  # will print the big comment above.
       return
    
    for o,a in opts:
       if o in ("-h", "--help"):
          print SWEAR.__doc__
          return
       else:
          assert False, "unhandled option"

    # Check for setup file in array args:
    if len(args) == 1:
        configfile = args[0]
        print swap.doubledashedline
        print swap.hello
        print swap.doubledashedline
        print "SWEAR: taking instructions from",configfile
    else:
        print SWEAR.__doc__
        return

    # ------------------------------------------------------------------
    # Read in run configuration:
    
    tonights = swap.Configuration(configfile)
       
    # Simple naming scheme for output lists and plots:
    tonights.parameters['trunk'] = \
        tonights.parameters['survey']

    tonights.parameters['dir'] = os.getcwd()
    
    # What was the last time a subject was touched?
    t = datetime.datetime.strptime(tonights.parameters['start'], '%Y-%m-%d_%H:%M:%S')
   
    # ------------------------------------------------------------------
    # Read in, or create, a bureau of agents who will represent the 
    # volunteers:
    
    bureau = swap.read_pickle(tonights.parameters['bureaufile'],'bureau')
   
    # ------------------------------------------------------------------
    # Read in, or create, an object representing the candidate list:
    
    sample = swap.read_pickle(tonights.parameters['samplefile'],'collection')
    
    # ------------------------------------------------------------------

    # Output list of subjects to retire, based on this batch of 
    # classifications. Note that what is needed here is the ZooID, 
    # not the subject ID. Also print out lists of detections etc! 
    # These are urls of images.

    new_samplefile = swap.get_new_filename(tonights.parameters,'candidates')
    print "SWEAR: saving lens candidates..."
    N = swap.write_list(sample,new_samplefile,item='candidate')
    print "SWEAR: "+str(N)+" lines written to "+new_samplefile

    # Now save the training images, for inspection: 
    new_samplefile = swap.get_new_filename(tonights.parameters,'training_true_positives')
    print "SWEAR: saving true positives..."
    N = swap.write_list(sample,new_samplefile,item='true_positive')
    print "SWEAR: "+str(N)+" lines written to "+new_samplefile

    new_samplefile = swap.get_new_filename(tonights.parameters,'training_false_positives')
    print "SWEAR: saving false positives..."
    N = swap.write_list(sample,new_samplefile,item='false_positive')
    print "SWEAR: "+str(N)+" lines written to "+new_samplefile

    new_samplefile = swap.get_new_filename(tonights.parameters,'training_false_negatives')
    print "SWEAR: saving false negatives..."
    N = swap.write_list(sample,new_samplefile,item='false_negative')
    print "SWEAR: "+str(N)+" lines written to "+new_samplefile

    # ------------------------------------------------------------------
    
    # Make plots! Can't plot everything - uniformly sample 200 of each
    # thing (agent or subject).

    # Agent histories:

    fig1 = bureau.start_history_plot()
    pngfile = swap.get_new_filename(tonights.parameters,'histories')
    Nc = np.min([200,bureau.size()])
    print "SWEAR: plotting "+str(Nc)+" agent histories in "+pngfile

    for Name in bureau.shortlist(Nc):
        bureau.member[Name].plot_history(fig1)

    bureau.finish_history_plot(fig1,t,pngfile)
    tonights.parameters['historiesplot'] = pngfile

    # Agent probabilities:

    pngfile = swap.get_new_filename(tonights.parameters,'probabilities')
    print "SWEAR: plotting "+str(Nc)+" agent probabilities in "+pngfile
    bureau.plot_probabilities(Nc,t,pngfile)        
    tonights.parameters['probabilitiesplot'] = pngfile

    # Subject probabilities:

    fig3 = sample.start_trajectory_plot()
    pngfile = swap.get_new_filename(tonights.parameters,'trajectories')
    Ns = np.min([500,sample.size()])
    print "SWEAR: plotting "+str(Ns)+" subject trajectories in "+pngfile

    for ID in sample.shortlist(Ns):
        sample.member[ID].plot_trajectory(fig3)

    sample.finish_trajectory_plot(fig3,t,pngfile)
    tonights.parameters['trajectoriesplot'] = pngfile

    # ------------------------------------------------------------------
    # Finally, write a PDF report:

    swap.write_report(tonights.parameters,bureau,sample) 

    # ------------------------------------------------------------------
    
    print swap.doubledashedline
    return

# ======================================================================

if __name__ == '__main__': 
    SWEAR(sys.argv[1:])

# ======================================================================
