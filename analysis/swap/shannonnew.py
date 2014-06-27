#============================================================================
"""
NAME
    shannon.py

PURPOSE
    Methods for calculating various information gains during binary 
    classification.

COMMENTS
	A different approach to calculating the information gain based on
    discussions between Anupreeta and Surhud

METHODS
    shannonEntropy(x)
    informationGain(p0, p1)
    expectedInformationGain(p0, M_ll, M_nn)

BUGS

AUTHORS
  The code in this file was written by Surhud More and Anupreeta More
  at home in June 2014.
  This file is part of the Space Warps project, which is distributed 
  under the GPL v2 by the Space Warps Science Team.
  http://spacewarps.org/

HISTORY
  2014-06-20  First version
  
LICENCE
  The MIT License (MIT)

  Copyright (c) 2014 Kavli IPMU

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

from numpy import log2, ndarray, where

# ----------------------------------------------------------------------------
# The Shannon information, I

def shannonEntropy(x):
    if isinstance(x, ndarray) == False:
        if x>0 and (1.-x)>0:
            return -x*log2(x)-(1.-x)*log2(1.-x)
        else:
            return 0.0

    x[x == 0] = 1.0
    res=-x*log2(x)

    x[x == 1] = 0.0

    return res-(1.-x)*log2(1.-x)

# ----------------------------------------------------------------------------
# The information contributed by an agent having classified a subject, that
# arrived having probability 'p0' and has new probability 'p1'

def informationGain(p0, p1):

    I = shannonEntropy(p0) - shannonEntropy(p1)

    return I

#============================================================================
# Expectation value of the information that would be contributed by an 
# agent defined by confusion matrix M when presented with a subject
# having probability p0, over both possible truths and both 
# possible classifications:

def expectedInformationGain(p0, M_ll, M_nn):
    p1=update(p0,M_ll,M_nn,1);
    info1=informationGain(p0,p1);
    
    p1=update(p0,M_ll,M_nn,0);
    info2=informationGain(p0,p1);

    probL=p0*M_ll+(1-p0)*(1-M_nn);
    probD=(1-p0)*M_nn+p0*(1-M_ll);

    return probL*info1+probD*info2;
 

# ----------------------------------------------------------------------------
# Bayesian update of the probability of a subject p0 by an agent whose
# confusion matrix is defined by M
def update(p0,M_ll,M_nn,lens):
    if isinstance(M_ll, ndarray) == False:
        if(lens):
            denom=(p0*M_ll+(1.-M_nn)*(1.-p0));
            if(denom==0):
                return p0;
            else:
                return p0*M_ll/denom;
        else:
            denom=(p0*(1-M_ll)+M_nn*(1.-p0));
            if(denom==0):
                return p0;
            else:
                return p0*(1-M_ll)/denom;
    else: 
        if(lens):
            denom=(p0*M_ll+(1.-M_nn)*(1.-p0));
            idx=where(denom==0);
            denom[idx]=1.0;
            postp0=p0*M_ll/denom;
            postp0[idx]=p0[idx];
            return postp0;
        else:
            idx=where(denom==0);
            denom[idx]=1.0;
            postp0=p0*(1-M_ll)/denom;
            postp0[idx]=p0[idx];
            return postp0;

# ----------------------------------------------------------------------------
if ( __name__ == "__main__"):
    
    #arr=np.reshape(np.array(101*101),(101,101)); 
    print expGain(0.5,0.3,0.2);
    print expGain(0.5,0.1,0.4);
    
