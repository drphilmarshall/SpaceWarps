#!/usr/bin/env python

import numpy as np
import cPickle,os,sys

# Command line arguments:
filename = sys.argv[1]
seed = sys.argv[2]

# Overwrite random state file:
try:
    os.remove(filename)
except OSError:
    pass

# Generate random state and pickle it:
pfile=open(filename,"w")
np.random.seed(int(seed))
cPickle.dump(np.random.RandomState().get_state(),pfile)
pfile.close()

# That's it.
