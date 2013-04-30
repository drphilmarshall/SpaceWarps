# ===========================================================================

import swap

import os,cPickle,atpy

# ======================================================================

"""
    NAME
        io

    PURPOSE
        Useful general functions to streamline file input and output.

    COMMENTS
            
    FUNCTIONS
        writePickle(contents,filename):
        
        readPickle(filename): returns contents of pickle
        
        readCatalog(filename,config): returns table, given column names
                                      in configuration config
    
        rm(filename): silent file removal
        
    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

      SWAP io is modelled on that written for the
      Pangloss project, by Tom Collett (IoA) and Phil Marshall (Oxford).
      https://github.com/drphilmarshall/Pangloss/blob/master/pangloss/io.py

    HISTORY
      2013-04-17  Started Marshall (Oxford)
"""

#=========================================================================
# Read in an instance of a class, of a given flavour. Create an instance 
# if the file does not exist.

def read_pickle(filename,flavour):
    
    try:
        F = open(filename,"rb")
        contents = cPickle.load(F)
        F.close()
        
    except:

        if filename is None: 
            print "SWAP: no "+flavour+" filename supplied."
        else:
            print "SWAP: "+filename+" does not exist."

        if flavour == 'crowd':
            contents = swap.Crowd()
            print "SWAP: made a new",contents

        elif flavour == 'collection':
            contents = swap.Collection()
            print "SWAP: made a new",contents
        
        elif flavour == 'database':
            contents = None
            
    return contents

# ----------------------------------------------------------------------------
# Write out an instance of a class to file.

def write_pickle(contents,filename):

    F = open(filename,"wb")
    cPickle.dump(contents,F,protocol=2)
    F.close()

    return

# ----------------------------------------------------------------------------
# Make up a new filename, based on tonight's parameters:

def get_new_filename(pars,flavour):

    head = pars['stem']+'_'+flavour
    if flavour == 'crowd' or flavour == 'collection' or flavour == 'database':
        ext = 'pickle'
    elif flavour == 'history' or flavour == 'trajectory' or flavour == 'probabilities':
        ext = 'png'
    else:
        raise Exception("SWAP: io: eww - what's that flavour? "+flavour)    
        
    return head+'.'+ext

# ----------------------------------------------------------------------------
# Remove file, if it exists, stay quiet otherwise:

def rm(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
    return
    
# ======================================================================
