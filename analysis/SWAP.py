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
        -h            Print this message
        -p --practise Do a dry run, using a simple toy model database

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
       opts, args = getopt.getopt(argv,"hp",["help","practise"])
    except getopt.GetoptError, err:
       print str(err) # will print something like "option -a not recognized"
       print SWAP.__doc__  # will print the big comment above.
       return

    practise = False
    
    for o,a in opts:
       if o in ("-h", "--help"):
          print SWAP.__doc__
          return
       elif o in ("-p", "--practise"):
          practise = True
       else:
          assert False, "unhandled option"

    # Check for setup file in array args:
    if len(args) == 1:
        configfile = args[0]
        print swap.doubledashedline
        print swap.hello
        print swap.doubledashedline
        print "SWAP: taking instructions from",configfile
        if practise:
            print "SWAP: doing a dry run using a Toy database"
        else:
            print "SWAP: data will be read from the current Mongo database"
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
    # Read in, or create, a bureau of agents who will represent the 
    # collaboration:
    
    collaboration = swap.read_pickle(tonights.parameters['crowdfile'],'crowd')
   
    # ------------------------------------------------------------------
    # Read in, or create, an object representing the candidate list:
    
    sample = swap.read_pickle(tonights.parameters['samplefile'],'collection')
        
    # ------------------------------------------------------------------
    # Open up database:
    
    if practise:
        db = swap.ToyDB(ambition=1)
    else:
        db = swap.MongoDB()

    # Read in a batch of classifications, since the specified time:
    
    t1 = datetime.datetime(1978, 2, 28, 12,0, 0, 0)

    batch = db.find('since',t1)
        
    # ------------------------------------------------------------------
   
    for classification in batch:

        # Get the vitals for this classification:
        t,Name,ID,category,kind,X,Y = db.digest(classification)

        # BUG! The above line fails, with error:
        #   TypeError: 'NoneType' object is not iterable


        # Register new volunteers, and create an agent for each one:
        if Name not in collaboration.list():  
            collaboration.member[Name] = swap.Classifier(Name)
            # Note that a collaboration.member is an *agent*, not a 
            # person. People exist in real life, whereas this is 
            # just a piece of software!
        
        # Register newly-classified subjects:
        if ID not in sample.list():           
            sample.member[ID] = swap.Subject(ID,category,kind,Y)    

        # Update the agent's confusion matrix, based on what it heard:
        if category == 'training':
            collaboration.member[Name].heard(it_was=X,actually_it_was=Y)

        # Update the subject's lens probability using input from the 
        # collaboration member. We send that member's agent to the subject
        # to do this.  
        sample.member[ID].was_described(by=collaboration.member[Name],as_being=X)

        # Brag about it:
        print "SWAP: --------------------------------------------------------------------------"
        print "SWAP: subject "+ID+" was classified by "+Name
        print "SWAP: he/she said "+X+" when it was actually "+Y
        print "SWAP: their agent reckons their contribution (in bits) = ",collaboration.member[Name].contribution
        print "SWAP: while estimating their PL,PD as ",collaboration.member[Name].PL,collaboration.member[Name].PD
        print "SWAP: and the subject's new probability as ",sample.member[ID].probability
       

    # ------------------------------------------------------------------
    # Make plots:
    
    # Agent histories:
    
    fig1 = collaboration.start_history_plot()
    for Name in collaboration.list():
        collaboration.member[Name].plot_history(fig1)
    pngfile = swap.get_new_filename(tonights.parameters,'history')
    collaboration.finish_history_plot(fig1,pngfile)
        
    # Subject probabilities:
    
    fig2 = sample.start_trajectory_plot()
    for ID in sample.list():
        sample.member[ID].plot_trajectory(fig2)
    pngfile = swap.get_new_filename(tonights.parameters,'trajectory')
    sample.finish_trajectory_plot(fig2,pngfile)
    
    # ------------------------------------------------------------------
    # Pickle the collaboration. Hooray! 

    new_crowdfile = swap.get_new_filename(tonights.parameters,'crowd')
    swap.write_pickle(collaboration,new_crowdfile)

    # ------------------------------------------------------------------
    
    print swap.doubledashedline
    return

# ======================================================================

if __name__ == '__main__': 
    SWAP(sys.argv[1:])

# ======================================================================
