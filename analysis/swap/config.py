# ===========================================================================

import os, glob

# ======================================================================
# Global parameters:

# Limits to subject probability (cannot go over 1 anyway):
pmin,pmax = 2e-8,1.1

# Plotting limits for no. of classifications (per subject):
Ncmin,Ncmax = 0.2,60

# Limits to confusion matrix elements - the volunteers are only human:
PDmax,PLmax = 0.99,0.99
PDmin,PLmin = 0.01,0.01
Imax = 0.919

# ======================================================================

class Configuration(object):
    """
    NAME
        Configuration

    PURPOSE
        Structure of metadata supplied by the SWAP user to define 
        the analysis they want to do.

    COMMENTS

    INITIALISATION
        configfile    Plain text file containing desired values of pars
    
    METHODS
        read(self): from configfile, get par names and values
        
        convert(self): strings to numbers, and expand paths
        
        prepare(self): set up workspace
        
    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

      SWAP configuration is modelled on that written for the
      Pangloss project, by Tom Collett (IoA) and Phil Marshall (Oxford).
      https://github.com/drphilmarshall/Pangloss/blob/master/pangloss/config.py

    HISTORY
      2013-04-03  Started Marshall (Oxford)
    """

    def __init__(self,configfile):
        self.file = configfile
        self.parameters = {}
        self.read()
        self.convert()
        self.prepare()
        return

    # ------------------------------------------------------------------
    # Read in values by keyword and populate the parameters dictionary.

    def read(self):
        thisfile = open(self.file)
        for line in thisfile:
            # Ignore truly empty lines and comments:
            if line[0:2] == '\n': continue
            if line[0] == '#': continue
            line.strip()
            line = line.split('#')[0]
            # Remove whitespace:
            line = ''.join(line.split())
            # Ignore lines without colons:
            if ':' not in line: continue
            # Interpret remaining lines, which contain Name:Value pairs:
            line = line.split(':')
            Name, Value = line[0], ':'.join(line[1:])
            # NB. We have to cope with strings that themselves contain 
            # colons - like timestamps.
            self.parameters[Name] = Value
        thisfile.close()
        return

    # ------------------------------------------------------------------
    # Convert string values into floats/ints where necessary, and expand
    # environment variables.

    def convert(self):

        # Some values need to be floats or integers:
        for key in self.parameters.keys():
            try:
                self.parameters[key] = float(self.parameters[key])
            except ValueError:
                pass
                            
            # Certain strings are special:
            if self.parameters[key] == 'False': 
                self.parameters[key] = False
            elif self.parameters[key] == 'True': 
                self.parameters[key] = True
            elif self.parameters[key] == 'None': 
                self.parameters[key] = None

        return

    # ------------------------------------------------------------------
    # Perform various other preparations.

    def prepare(self):

        # Make directories if necessary:
        # folderkeys = ['CalibrationFolder']
        # for key in folderkeys:
        #     folder = self.parameters[key]
        #     fail = os.system('mkdir -p '+folder[0])

        return

# ======================================================================

