#!/usr/bin/env python
# ======================================================================

import swap

import sys,getopt,time
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

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-05-07 started. Marshall (Oxford)
      2013-08-05 added whitelist, not to be reactivated. Marshall (KIPAC)
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
    
    if resurrect:
        print "SWITCH: looks like we have",len(IDs)," subjects to resurrect"
    else:
        print "SWITCH: looks like we have",len(IDs)," subjects to retire"

    
    if practise: print "SWITCH: doing a dry run"
    
    # Set up whitelist, not to be resurrected:
    whitelist = ['ASW0000001', 'ASW0000002', 'ASW0000003', 'ASW0000004', \
                 'ASW0000005', 'ASW0000006', 'ASW0000007', 'ASW0000009', \
                 'ASW000000a', 'ASW000000b', 'ASW000000c', 'ASW000000d', \
                 'ASW000000e', 'ASW000000f' ]
    
    # ------------------------------------------------------------------
    # Create a client called "philmarshall", using stuff from client.py:
            
    client = Client('philmarshall', password, private_key)
    
    # ------------------------------------------------------------------
    
    for ID in IDs:
    
         if resurrect:
             down = '/projects/spacewarp/subjects/'+ID+'/activate'
         else:
             down = '/projects/spacewarp/subjects/'+ID+'/retire'
    
         # Ignore whitelist:
         if ((ID in whitelist) and resurrect):
             print "SWITCH: resurrection attempt ignored: ",ID
             pass
             
         else:
         # Send the message!
             
             if practise:
                 print "result = client.put('"+down+"')"

             else:
                 worked = client.put(down)
                 time.sleep(0.8) # So that we don't go over 5000 per hour.
                 if not worked:
                     print "SWITCH: retirement fail: ",ID,worked
                 else:
                     if resurrect:
                         print "SWITCH: successfully resurrected subject "+ID
                     else:
                         print "SWITCH: successfully retired subject "+ID
                 
    # ------------------------------------------------------------------
    print swap.doubledashedline
    return

# ======================================================================

if __name__ == '__main__': 
    SWITCH(sys.argv[1:])

# ======================================================================
