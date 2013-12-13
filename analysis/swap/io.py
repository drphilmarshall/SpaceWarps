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
        
        print "SWAP: read an old",contents,"from "+filename
        
    except:

        if filename is None: 
            print "SWAP: no "+flavour+" filename supplied."
        else:
            print "SWAP: "+filename+" does not exist."

        if flavour == 'bureau':
            contents = swap.Bureau()
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
# Write out a simple list of subject IDs, of subjects to be retired.

def write_list(sample, filename, item=None):

    count = 0
    F = open(filename,'w')
    for ID in sample.list():
        subject = sample.member[ID]
        string = None
        
        if item == 'retired_subject':
            if subject.state == 'inactive':
                string = subject.ZooID
            
        elif item == 'candidate':
            if subject.kind == 'test' and subject.status == 'detected':
                string = subject.location
            
        elif item == 'true_positive':
            if subject.kind == 'sim' and subject.status == 'detected':
                string = subject.location
            
        elif item == 'false_positive':
            if subject.kind == 'dud' and subject.status == 'detected':
                string = subject.location
            
        elif item == 'true_negative':
            if subject.kind == 'dud' and subject.status == 'rejected':
                string = subject.location
            
        elif item == 'false_negative':
            if subject.kind == 'sim' and subject.status == 'rejected':
                string = subject.location
            
        # Write a new line:
        if item is not None and string is not None:
            F.write('%s\n' % string)
            count += 1
    
    F.close()
        
    return count
    
# ----------------------------------------------------------------------------
# Write out a multi-column catalog of high probability candidates.

def write_catalog(sample, filename, thresholds, kind='test'):

    Nsubjects = 0
    Nlenses = 0
    
    # Open a new catalog and write a header:
    F = open(filename,'w')
    F.write('%s\n' % "# zooid     P          Nclass  image")
    
    for ID in sample.list():
        subject = sample.member[ID]
        P = subject.mean_probability
        
        if P > thresholds['rejection'] and subject.kind == kind:
        
            zooid = subject.ZooID
            png = subject.location
            Nclass = subject.exposure

            # Write a new line:
            F.write('%s  %9.7f  %s       %s\n' % (zooid,P,str(Nclass),png))
            Nlenses += 1
    
        Nsubjects += 1
    
    F.close()
        
    return Nlenses,Nsubjects
    
# ----------------------------------------------------------------------------
# Make up a new filename, based on tonight's parameters:

def get_new_filename(pars,flavour):

    # Usually, this is what we want filenames to look like:
    stem = pars['trunk']+'_'+flavour
    # Pickles are an exception though!
    
    if flavour == 'bureau' or \
         flavour == 'collection' or \
         flavour == 'database':
        stem = pars['survey']+'_'+flavour
        ext = 'pickle'
        folder = '.'
    elif flavour == 'histories' or \
         flavour == 'trajectories' or \
         flavour == 'sample' or \
         flavour == 'probabilities':
        ext = 'png'
        folder = pars['dir']
    elif flavour == 'retire_these':
        ext = 'txt'
        folder = pars['dir']
    elif flavour == 'candidate_catalog' or \
         flavour == 'sim_catalog' or \
         flavour == 'dud_catalog':
        ext = 'txt'
        folder = pars['dir']
    elif flavour == 'candidates' or \
         flavour == 'training_true_positives' or \
         flavour == 'training_false_positives' or \
         flavour == 'training_true_negatives' or \
         flavour == 'training_false_negatives':
        ext = 'txt'
        folder = pars['dir']
    else:
        raise Exception("SWAP: io: unknown flavour "+flavour)    
        
    return folder+'/'+stem+'.'+ext

# ----------------------------------------------------------------------------
# Write configuration file given a dictionary of parameters:
 
def write_config(filename, pars):

    F = open(filename,'w')

    header = """
# ======================================================================
#
# Space Warps Analysis Pipeline configuration file.
#
# Lines starting with '#' are ignored; all other lines must contain a
# Name : Value pair to be read into the parameters dictionary.
#
# This file is part of the Space Warps project, and is distributed 
# under the GPL v2 by the Space Warps Science Team.
# http://spacewarps.org/
# 
# SWAP configuration is modelled on that written for the
# Pangloss project, by Tom Collett (IoA) and Phil Marshall (Oxford). 
# https://github.com/drphilmarshall/Pangloss/blob/master/example/example.config
#
# ======================================================================
    """
    F.write(header)
   
    shortlist = ['survey', \
                 'start', \
                 'bureaufile', \
                 'samplefile', \
                 'stage', \
                 'verbose', \
                 'one_by_one', \
                 'report', \
                 'repickle', \
                 'initialPL', \
                 'initialPD', \
                 'agents_willing_to_learn', \
                 'a_few_at_the_start', \
                 'hasty', \
                 'skepticism', \
                 'use_marker_positions', \
                 'detection_threshold', \
                 'rejection_threshold', \
                 'dbspecies']
   
    for keyword in shortlist:
        F.write('\n')
        F.write('%s: %s\n' % (keyword,str(pars[keyword])))

    F.write('\n')
    footer = '# ======================================================================'
    F.write(footer)

    F.close()

    return

# ----------------------------------------------------------------------------
# Remove file, if it exists, stay quiet otherwise:

def rm(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
    return
    
# ======================================================================
