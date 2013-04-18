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
        
    except IOError:

        if filename != 'None': print "SWAP: "+filename+" does not exist."

        if flavour == 'crowd':
            contents = swap.Crowd()

        elif flavour == 'collection':
            contents = swap.Collection()
        
        print "SWAP: Made a new",contents
            
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

    head = pars['survey']+'_'+pars['t2string']+'_'+flavour
    if flavour == 'crowd':
        ext = 'pickle'
    elif flavour == 'history' or flavour == 'trajectory':
        ext = 'png'
    else:
        raise Exception("SWAP: io: eww - what's that flavour? "+flavour)    
        
    return head+'.'+ext

# ----------------------------------------------------------------------------
# 
# def readCatalog(filename,config):
# 
#     table = atpy.Table(filename, type='ascii')
# 
#     try: table.rename_column(config.parameters['nRAName'],'nRA')
#     except: pass
#     try: table.rename_column(config.parameters['DecName'],'Dec')
#     except: pass
# 
#     # Calibration catalogs:
#     try: table.rename_column(config.parameters['CalibMhaloName'],'Mhalo_obs')
#     except: pass
#     try: table.rename_column(config.parameters['CalibRedshiftName'],'z_obs')
#     except: pass
# 
#     # Observed catalog:
#     try: table.rename_column(config.parameters['ObsMstarName'],'Mstar_obs')
#     except: pass
#     try: table.rename_column(config.parameters['ObsRedshiftName'],'z_obs')
#     except: pass
#     try: 
#         mag = table[config.parameters['MagName']]
#         table.add_column('mag',mag)
#     except: 
#         raise "Error in io.readCatalog: no mag column called "+config.parameters['MagName']
#    
#     return table
# 
# ----------------------------------------------------------------------------
# Remove file, if it exists, stay quiet otherwise:

def rm(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
    return
    
# ======================================================================
