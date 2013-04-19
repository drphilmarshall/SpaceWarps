#!/usr/bin/env python
# ======================================================================

import swap

import sys,getopt,datetime

# ======================================================================

def SWAP(argv):
    """
    NAME
        SWAP.py

    PURPOSE
        Space Warps Analysis Pipeline
        
        Read in a Space Warps classification database from a MongoDB 
        database, and analyse it.

    COMMENTS
        The SW analysis is "online" in the statistical sense: we step 
        through the classifications one by one, updating each
        classifier's confusion matrix and each subject's lens
        probability. The main reason for taking this approach is that
        it is the most logical one; secondarily, it opens up the
        possibility of performing the analysis in real time (although
        presumably not with this piece of python).

        Amit: can you help us get started please? Search for the string
        MONGO to see where I need help extracting information from the
        mongo DB.

        Currently, the confusion matrices only depend on the
        classifications of training subjects. Upgrading this would be a
        nice piece of further work. Likewise, neither the Marker
        positions, the classification  durations, nor any other
        parameters are used in estimating lens probability - but they
        could be. In this version, it's LENS or NOT.

        Standard operation is to update the candidate list by making a
        new, timestamped catalog of candidates - and the
        classifications that led to them. This means we have to know
        when the last update was made - this is done by reading in a
        pickle of the last classification to be SWAPped. The final
        sample of candidates could be obtained by reading  in all
        sample pickles and taking the most up to date characterisation
        of  each - but we might as well over-write a pickle of this
        every time too. The crowd we have to always read in in its
        entirety, because they can reappear any time to update their
        confusion matrices.
        
    FLAGS
        -h            Print this message [0]

    INPUTS
        configfile    Plain text file containing SW experiment configuration

    OUTPUTS
        stdout
        theCrowd.pickle
        theLensSampleFrom.DATE.pickle
        theClassificationBatchFrom.DATE.pickle
        theMostRecentClassification.pickle

    EXAMPLE
        
        cd workspace
        SWAP.py CFHTLS-beta-day01.config > CFHTLS-beta-day01.log

    BUGS
        - No capability to read MongoDB yet.
        - No actual analysis routines coded.

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-03 started. Marshall (Oxford)
      2013-04-17 implemented v1 "LENS or NOT" analysis. Marshall (Oxford)
    """

    # ------------------------------------------------------------------

    try:
       opts, args = getopt.getopt(argv,"h",["help"])
    except getopt.GetoptError, err:
       print str(err) # will print something like "option -a not recognized"
       print SWAP.__doc__  # will print the big comment above.
       return

    for o,a in opts:
       if o in ("-h", "--help"):
          print SWAP.__doc__
          return
       else:
          assert False, "unhandled option"

    # Check for setup file in array args:
    if len(args) == 1:
        configfile = args[0]
        print swap.doubledashedline
        print swap.hello
        print swap.doubledashedline
        print "SWAP: taking instructions from",configfile
        print "SWAP: for the actual analysis, we need a DB and some code from Amit!"
        print "SWAP: more on this soon..."
        print "SWAP: for now, just make some useful objects."
    else:
        print SWAP.__doc__
        return

    # ------------------------------------------------------------------
    # Read in run configuration:
    
    tonights = swap.Configuration(configfile)
    
    if tonights.parameters['time'] == 'Now':
        tonights.parameters['t2'] = datetime.datetime.utcnow()
        tonights.parameters['t2string'] = tonights.parameters['t2'].strftime("%Y-%m-%d_%H%M")
        print "SWAP: updating all objects with classifications up to "+tonights.parameters['t2string']
    else:
        raise "SWAP: analysis between 2 points in time not yet implemented"
    
    # ------------------------------------------------------------------
    # Read in, or create, an object representing the crowd:
    
    collaboration = swap.read_pickle(tonights.parameters['crowdfile'],'crowd')

    # Start a plot of their histories:
    
    fig1 = collaboration.start_history_plot()
    
    # ------------------------------------------------------------------
    # Read in, or create, an object representing the candidate list:
    
    sample = swap.read_pickle(tonights.parameters['samplefile'],'collection')
    
    # Start a plot of their probabilities:
    
    fig2 = sample.start_trajectory_plot()
    
    # ------------------------------------------------------------------
   
    for k in range(6):
    
        # Pull out a fake classification:
        if k == 0: 
            Name,ID,category,X,Y = ('Phil1','0001' ,'training','NOT','LENS')
        if k == 1: 
            Name,ID,category,X,Y = ('Phil2','0001' ,'training','LENS','LENS')
        if k == 2: 
            Name,ID,category,X,Y = ('Phil1','0002' ,'training','LENS','NOT')
        if k == 3: 
            Name,ID,category,X,Y = ('Phil1','0003' ,'training','LENS','LENS')
        if k == 4: 
            Name,ID,category,X,Y = ('Phil2','0002' ,'training','LENS','NOT')
        if k == 5: 
            Name,ID,category,X,Y = ('Phil2','0003' ,'training','NOT','LENS')

        # Register new members:
        if Name not in collaboration.list():  
            collaboration.member[Name] = swap.Classifier(Name)
        if ID not in sample.list():           
            sample.member[ID] = swap.Subject(ID,category,kind=Y)    

        # Update the classifier's confusion matrix:
        if category == 'training':
            collaboration.member[Name].said(it_was=X,actually_it_was=Y)

        # Update the subject's lens probability:
        sample.member[ID].described(by=collaboration.member[Name],as_kind=X)

        # Brag about it:
        print "SWAP: subject "+ID+" was classified by "+Name
        print "SWAP: he said",X," when it was ",Y,": expertise,PL,PD = ", \
            collaboration.member[Name].expertise,collaboration.member[Name].PL,collaboration.member[Name].PD
        print "SWAP: its new probability = ",sample.member[ID].probability
       

    # ------------------------------------------------------------------
    # Make plots:
    
    for Name in collaboration.list():
        collaboration.member[Name].plot_history(fig1)
        
    for ID in sample.list():
        sample.member[ID].plot_trajectory(fig2)
    

    # ------------------------------------------------------------------
    # Pickle the collaboration. Hooray! 

    new_crowdfile = swap.get_new_filename(tonights.parameters,'crowd')
    swap.write_pickle(collaboration,new_crowdfile)


    # ------------------------------------------------------------------
    # Write out plots to pngfiles:
    
    pngfile = swap.get_new_filename(tonights.parameters,'history')
    collaboration.finish_history_plot(fig1,pngfile)
    
    pngfile = swap.get_new_filename(tonights.parameters,'trajectory')
    sample.finish_trajectory_plot(fig2,pngfile)
    
    
    # ------------------------------------------------------------------
    
    print swap.doubledashedline
    return

# ======================================================================

if __name__ == '__main__': 
    SWAP(sys.argv[1:])

# ======================================================================
