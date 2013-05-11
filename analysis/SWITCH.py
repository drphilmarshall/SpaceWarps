#!/usr/bin/env python
# ======================================================================

import swap

import sys,getopt
import numpy as np

from client import *

# ======================================================================

def SWITCH(argv):
    """
    NAME
        SWITCH.py

    PURPOSE
        Space Warps retirement plan. Take in a list of Zooniverse 
        subject IDs, and set their states to inactive. 

    COMMENTS
        This script was kept separate from SWAP on the grounds that
        we'll want to do some analysis runs while *not* influencing the
        database at Adler. Seems sensible to keep the two scripts 
        separate, for different goals.
        
    FLAGS
        -h                Print this message
        -p --practise     Don't do the put, just print the commands
        -r --resurrect    Re-activate subject

    INPUTS
        ids.txt           Plain text file containing list of subject IDs
    
    OUTPUTS
        stdout

    EXAMPLE
        
        SWITCH.py CFHTLS_2013-05-07/CFHTLS_2013-05-07_retire_these.txt

    BUGS
        - Untested.

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-05-07 started: Marshall (Oxford)
    """

    # ------------------------------------------------------------------

    try:
       opts, args = getopt.getopt(argv,"hpr",["help","practise","resurrect"])
    except getopt.GetoptError, err:
       print str(err) # will print something like "option -a not recognized"
       print SWITCH.__doc__  # will print the big comment above.
       return
    
    practise = False
    resurrect = False

    for o,a in opts:
       if o in ("-h", "--help"):
          print SWITCH.__doc__
          return
       elif o in ("-p", "--practise"):
          practise = True
       elif o in ("-r", "--resurrect"):
          resurrect = True
       else:
          assert False, "unhandled option"

    # Check for setup file in array args:
    if len(args) == 1:
        listfile = args[0]
        print swap.doubledashedline
        print swap.helloswitch
        print swap.doubledashedline
        print "SWITCH: retiring subjects listed in ",listfile
    else:
        print SWITCH.__doc__
        return

    # ------------------------------------------------------------------
    # Read in subjects:
    
    IDs = np.genfromtxt(listfile,dtype='str')
    
    print "SWITCH: looks like we have",len(IDs)," subjects to retire"
    
    if practise: print "SWITCH: doing a dry run"
    
    # ------------------------------------------------------------------
    # Create a client called "philmarshall", using stuff from client.py:
            
    client = Client('philmarshall', password, private_key)
    
    # ------------------------------------------------------------------
    
    for ID in IDs:
    
         if resurrect:
         
             down = '/projects/spacewarp/subjects/'+ID+'/wtf'
         else:
             down = '/projects/spacewarp/subjects/'+ID+'/retire'
    
         if practise:
             print "result = client.put('"+down+"')"
         
         else:
             worked = client.put(down)
             if not worked:
                 print "SWITCH: retirement fail: ",ID,worked
             else:
                 print "SWITCH: successfully retired subject "+ID
         
    # ------------------------------------------------------------------
    print swap.doubledashedline
    return

# ======================================================================

if __name__ == '__main__': 
    SWITCH(sys.argv[1:])

# ======================================================================
