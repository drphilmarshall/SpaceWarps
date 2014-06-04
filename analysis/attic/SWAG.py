#!/usr/bin/env python
# ======================================================================

import swap

import sys,getopt,datetime,os,subprocess
import numpy as np

# ======================================================================

def SWAG(argv):
    """
    NAME
        SWAG.py

    PURPOSE
        Read in a Space Warps candidates, and prepare catalog and 
        plots.

    COMMENTS
        
        
    FLAGS
        -h            Print this message

    INPUTS
        configfile    Plain text file containing SW experiment configuration

    OUTPUTS
        stdout
        *.png

    EXAMPLE
        
        SWAG.py update.config

    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-11-27  started. Marshall (KIPAC)
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
        print "SWAG: taking instructions from",configfile
    else:
        print SWAG.__doc__
        return

    # ------------------------------------------------------------------
    # Read in run configuration:
    
    tonights = swap.Configuration(configfile)
    
    thresholds = {}
    thresholds['detection'] = tonights.parameters['detection_threshold']
    thresholds['rejection'] = tonights.parameters['rejection_threshold']

    # Use the following directory for output lists and plots:
    tonights.parameters['trunk'] = tonights.parameters['survey']
    tonights.parameters['dir'] = '.'
    
    # ------------------------------------------------------------------
    # Read in, or create, an object representing the candidate list:
    
    print "SWAG: reading in subjects..."
    sample = swap.read_pickle(tonights.parameters['samplefile'],'collection')
                
    # ------------------------------------------------------------------

    # Write out a catalog of subjects, including the ZooID, subject ID,
    # how many classifications, and probability:

    catalog = swap.get_new_filename(tonights.parameters,'candidate_catalog')
    print "SWAG: saving catalog of high probability subjects..."
    Nlenses,Nsubjects = swap.write_catalog(sample,catalog,thresholds,kind='test')
    print "SWAG: "+str(Nsubjects)+" subjects classified,"
    print "SWAG: "+str(Nlenses)+" candidates (with P > rejection) written to "+catalog

    # Also write out the sims, and the duds:

    catalog = swap.get_new_filename(tonights.parameters,'sim_catalog')
    print "SWAG: saving catalog of high probability subjects..."
    Nsims,Nsubjects = swap.write_catalog(sample,catalog,thresholds,kind='sim')
    print "SWAG: "+str(Nsubjects)+" subjects classified,"
    print "SWAG: "+str(Nsims)+" sim 'candidates' (with P > rejection) written to "+catalog

    catalog = swap.get_new_filename(tonights.parameters,'dud_catalog')
    print "SWAG: saving catalog of high probability subjects..."
    Nduds,Nsubjects = swap.write_catalog(sample,catalog,thresholds,kind='dud')
    print "SWAG: "+str(Nsubjects)+" subjects classified,"
    print "SWAG: "+str(Nduds)+" dud 'candidates' (with P > rejection) written to "+catalog


    # ------------------------------------------------------------------

    # Histogram of probabilities, with scatterplot of Nclass .

    # Subject probabilities:

    pngfile = swap.get_new_filename(tonights.parameters,'sample')
    print "SWAP: plotting candidate histograms in "+pngfile

    collection.plot_sample(pngfile)

    # ------------------------------------------------------------------
    
    print swap.doubledashedline
    return

# ======================================================================

if __name__ == '__main__': 
    SWAG(sys.argv[1:])

# ======================================================================
