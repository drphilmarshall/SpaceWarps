#============================================================================
"""
NAME
    shannon.py

PURPOSE
    Methods for calculating various information gains during binary 
    classification.

COMMENTS
    Copied from informationgain.py at 
    https://github.com/CitizenScienceInAstronomyWorkshop/Bureaucracy 

METHODS
    shannon(x):
    expectedInformationGain(p0, M_ll, M_nn)
    informationGain(p0, M_ll, M_nn, c)

BUGS

AUTHORS
  The code in this file was written by Edwin Simpson and Phil Marshall
  during the Citizen Science in Astronomy Workshop at ASIAA, Taipei, 
  in March 2014, hosted by Meg Schwamb. 
  This file is part of the Space Warps project, which is distributed 
  under the GPL v2 by the Space Warps Science Team.
  http://spacewarps.org/

HISTORY
  2014-05-21  Incorporated into SWAP code Baumer & Davis (KIPAC)
  
LICENCE
  The MIT License (MIT)

  Copyright (c) 2014 CitizenScienceInAstronomyWorkshop

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
"""
#============================================================================

from numpy import log2, ndarray

# ----------------------------------------------------------------------------
# The Shannon information, I

def shannon(x):
    if isinstance(x, ndarray) == False:
        if x>0:
            return x*log2(x)
        else:
            return 0.0
    x[x == 0] = 1.0
    return x*log2(x)

# ----------------------------------------------------------------------------
# Expectation value of the information that would be contributed by an 
# agent defined by confusion matrix M when presented with a subject
# having probability p0, over both possible truths and both 
# possible classifications:

def expectedInformationGain(p0, M_ll, M_nn):
    p1 = 1-p0

    I = p0 * (shannon(M_ll) + shannon(1-M_ll)) + \
        p1 * (shannon(M_nn) + shannon(1-M_nn)) - \
        shannon(M_ll*p0 + (1-M_nn)*p1) - \
        shannon((1-M_ll)*p0 + M_nn*p1)

    return I

# ----------------------------------------------------------------------------
# The information contributed by an agent, defined by confusion matrix M,
# having classified a subject, that arrived having probability 'p0', 
# as being 'c' (true/false):

def informationGain(p0, M_ll, M_nn, c):
    p1 = 1-p0

    if c:
        M_cl = M_ll
        M_cn = 1-M_nn
    else:
        M_cl = 1-M_ll
        M_cn = M_nn

    pc = M_cl*p0 + M_cn*p1

    p0_c = M_cl/pc
    p1_c = M_cn/pc

    I = p0*shannon(p0_c) + p1*shannon(p1_c)

    return I

#============================================================================
