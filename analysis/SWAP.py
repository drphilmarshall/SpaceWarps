#!/usr/bin/env python
# ======================================================================

import swap

import sys,getopt,datetime,os,subprocess
import numpy as np

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
    else:
        print SWAP.__doc__
        return

    # ------------------------------------------------------------------
    # Read in run configuration:
    
    tonights = swap.Configuration(configfile)
    
    practise = (tonights.parameters['dbspecies'] == 'Toy')
    if practise:
        print "SWAP: doing a dry run using a Toy database"
    else:
        print "SWAP: data will be read from the current Mongo database"
    
    agents_willing_to_learn = tonights.parameters['agents_willing_to_learn']
    if agents_willing_to_learn:
        print "SWAP: agents will update their confusion matrices as new data arrives"
    else:
        print "SWAP: agents will use current confusion matrices without updating them"
    
    vb = tonights.parameters['verbose']
    if not vb: 
        print "SWAP: only reporting minimal stdout."
    
    # From when shall we take classifications to analyze?
    if tonights.parameters['start'] == 'the_beginning':
        t1 = datetime.datetime(1978, 2, 28, 12, 0, 0, 0)
    else:
        t1 = datetime.datetime.strptime(tonights.parameters['start'], '%Y-%m-%d')
    print "SWAP: updating all subjects with classifications made since "+tonights.parameters['start']
    
    # And what will we call the new files we make?
    t2 = datetime.datetime.utcnow()
    tonights.parameters['finish'] = t2.strftime('%Y-%m-%d')
    
    # Use the following stem for all output files:
    trunk = tonights.parameters['survey']+'_'+tonights.parameters['finish']
    tonights.parameters['dir'] = os.getcwd()+'/'+trunk
    subprocess.call(["mkdir","-p",tonights.parameters['dir']])
    tonights.parameters['stem'] = tonights.parameters['dir']+'/'+trunk

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
        
        db = swap.read_pickle(tonights.parameters['dbfile'],'database')
        
        if db is None:
            print "SWAP: making a new Toy database..."
            db = swap.ToyDB(pars=tonights.parameters)
        
        print "SWAP: database has ",db.size()," Toy classifications"
        print "SWAP: made by ",db.population," Toy classifiers"
        print "SWAP: of ",db.surveysize," Toy subjects"
        print "SWAP: where each classifier makes ",db.enthusiasm," classifications, on average"
       
    else:
        db = swap.MongoDB()

    # Read in a batch of classifications, made since the aforementioned 
    # start time:

    batch = db.find('since',t1)
        
    # ------------------------------------------------------------------
    
    print "SWAP: interpreting classifications..."
 
    count = 0
    for classification in batch:

        # Get the vitals for this classification:
        items = db.digest(classification)
        if items is None: 
            continue # Tutorial subjects fail!
        t,Name,ID,category,kind,X,Y = items

        # Register new volunteers, and create an agent for each one:
        if Name not in collaboration.list():  
            collaboration.member[Name] = swap.Classifier(Name,tonights.parameters)
            # Note that a collaboration.member is an *agent*, not a 
            # person. People exist in real life, whereas this is 
            # just a piece of software!
        
        # Register newly-classified subjects:
        if ID not in sample.list():           
            sample.member[ID] = swap.Subject(ID,category,kind,Y)    

        # Update the subject's lens probability using input from the 
        # collaboration member. We send that member's agent to the subject
        # to do this.  
        sample.member[ID].was_described(by=collaboration.member[Name],as_being=X)

        # Update the agent's confusion matrix, based on what it heard:
        if category == 'training' and agents_willing_to_learn:
            collaboration.member[Name].heard(it_was=X,actually_it_was=Y,ignore=False)
        elif category == 'training':
            collaboration.member[Name].heard(it_was=X,actually_it_was=Y,ignore=True)

        # Brag about it:
        count += 1
        if vb:
            print swap.dashedline
            print "SWAP: Subject "+ID+" was classified by "+Name
            print "SWAP: he/she said "+X+" when it was actually "+Y
            print "SWAP: their agent reckons their contribution (in bits) = ",collaboration.member[Name].contribution
            print "SWAP: while estimating their PL,PD as ",collaboration.member[Name].PL,collaboration.member[Name].PD
            print "SWAP: and the subject's new probability as ",sample.member[ID].probability
        else:
            # Count up to 74 in dots:
            if count == 1: sys.stdout.write('SWAP: ')
            elif np.mod(count,int(db.size()/73.0)) == 0: sys.stdout.write('.')
            elif count == db.size(): sys.stdout.write('\n')
            sys.stdout.flush()
        
    if vb: print swap.dashedline
    print "SWAP: total no. of classifications processed: ",count

    # ------------------------------------------------------------------
    # Pickle the collaboration and sample, if required:

    if tonights.parameters['repickle']:
    
        new_crowdfile = swap.get_new_filename(tonights.parameters,'crowd')
        print "SWAP: saving agents in "+new_crowdfile
        swap.write_pickle(collaboration,new_crowdfile)

        new_samplefile = swap.get_new_filename(tonights.parameters,'collection')
        print "SWAP: saving subjects in "+new_samplefile
        swap.write_pickle(sample,new_samplefile)

        new_dbfile = swap.get_new_filename(tonights.parameters,'database')
        print "SWAP: saving database in "+new_dbfile
        swap.write_pickle(db,new_dbfile)

    # ------------------------------------------------------------------
    # Make plots:
    
    # Agent histories:
    
    fig1 = collaboration.start_history_plot()
    pngfile = swap.get_new_filename(tonights.parameters,'history')
    Nc = np.min([1000,collaboration.size()])
    print "SWAP: plotting "+str(Nc)+" classifier histories in "+pngfile
    
    for Name in collaboration.shortlist(Nc):
        collaboration.member[Name].plot_history(fig1)
    collaboration.finish_history_plot(fig1,pngfile)
    tonights.parameters['historiesplot'] = pngfile

    # Agent probabilities:
    
    pngfile = swap.get_new_filename(tonights.parameters,'probabilities')
    print "SWAP: plotting "+str(Nc)+" classifier probabilities in "+pngfile
    collaboration.plot_histogram(pngfile)        
    tonights.parameters['probabilitiesplot'] = pngfile

    # Subject probabilities:
    
    fig3 = sample.start_trajectory_plot()
    pngfile = swap.get_new_filename(tonights.parameters,'trajectory')
    Ns = np.min([1000,sample.size()])
    print "SWAP: plotting "+str(Ns)+" subject trajectories in "+pngfile
    for ID in sample.shortlist(Ns):
        sample.member[ID].plot_trajectory(fig3)
    sample.finish_trajectory_plot(fig3,pngfile)
    tonights.parameters['trajectoriesplot'] = pngfile
    
    # ------------------------------------------------------------------
    # Write a PDF report:
    
    swap.write_report(tonights.parameters,collaboration,sample) 
    
    # ------------------------------------------------------------------
    
    print swap.doubledashedline
    return

# ======================================================================

if __name__ == '__main__': 
    SWAP(sys.argv[1:])

# ======================================================================
