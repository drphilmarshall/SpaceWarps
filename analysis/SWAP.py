#!/usr/bin/env python
# ======================================================================

import swap

import sys,getopt

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
        Amit: can you help us get started please? Ideally I would like
        us to read in the database as an atpy Table.
        
        We have various quality control metrics that need to be 
        computed, before outputting a ranked list of lens candidates. 
        The quality control methods make use of the numerous simulated 
        lenses, and known "dud" fields.

    FLAGS
        -h            Print this message [0]

    INPUTS
        configfile    Plain text file containing SW experiment configuration

    OUTPUTS
        stdout        Useful information, redirect this to a logfile
        candidates    Catalog of lens candidates, with associated stats

    EXAMPLE
        
        cd workspace
        SWAP.py CFHTLS-beta.config > CFHTLS-beta_SWAP.log

    BUGS
        - No capability to read MongoDB yet.
        - No actual analysis routines coded.

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-03 started Marshall (Oxford)
    """

    # --------------------------------------------------------------------

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
        print "SWAP: more soon..."
    else:
        print SWAP.__doc__
        return

    # --------------------------------------------------------------------
    # Read in configuration:
    
    # experiment = swap.Configuration(configfile)

    # --------------------------------------------------------------------
    # Load in database as a swap object:

    # clicks = swap.ClickDB(experiment.DBfile)
    
    # --------------------------------------------------------------------
    # Quality control:

    
    # --------------------------------------------------------------------
    # Lens candidate ranking:

    
    # --------------------------------------------------------------------
   
    print swap.doubledashedline
    return

# ======================================================================

if __name__ == '__main__': 
    SWAP(sys.argv[1:])

# ======================================================================
