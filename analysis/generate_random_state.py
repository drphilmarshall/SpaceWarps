#!/usr/bin/env python

import numpy as np;
import cPickle;
import sys;

pfile=open(sys.argv[1],"w");
np.random.seed(int(sys.argv[2]));
cPickle.dump(np.random.RandomState().get_state(),pfile);
pfile.close();
