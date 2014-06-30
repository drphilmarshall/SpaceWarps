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
    entropyChange(p0, M_ll, M_nn, c)
    mutualInformation(p0, p1)
    informationGain(p0, M_ll, M_nn, c)
    expectedInformationGain(p0, M_ll, M_nn)
    update(p0,M_ll,M_nn,c)

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

import numpy as np

# ----------------------------------------------------------------------------
# The Shannon function:

def shannon(x):

    if isinstance(x, np.ndarray) == False:

        if x>0:
            res = x*np.log2(x)
        else:
            res = 0.0
    
    else:
        x[x == 0] = 1.0
        res = x*np.log2(x)

    return res

# ----------------------------------------------------------------------------
# The Shannon entropy, S

def shannonEntropy(x):

    if isinstance(x, np.ndarray) == False:

        if x>0 and (1.-x)>0:
            res = -x*np.log2(x) - (1.-x)*np.log2(1.-x)
        else:
            res = 0.0
    
    else:
    
        x[x == 0] = 1.0
        res = -x*np.log2(x)

        x[x == 1] = 0.0
        res = res - (1.-x)*np.log2(1.-x)
       
    return res

# ----------------------------------------------------------------------------
# The change in subject entropy transmitted by an agent, having classified a 
# subject, that arrived having probability 'p0' and has new 
# probability 'p1'

def entropyChange(p0, M_ll, M_nn, c):

    p1 = update(p0,M_ll,M_nn,c)

    I = mutualInformation(p0,p1)

    return I

# ----------------------------------------------------------------------------
# The mutual information between states with probability 'p0' and 'p1'

def mutualInformation(p0,p1):

    I = shannonEntropy(p0) - shannonEntropy(p1)

    return I

# ----------------------------------------------------------------------------
# Expectation value of the information that would be contributed by an 
# agent defined by confusion matrix M when presented with a subject
# having probability p0, over both possible truths and both 
# possible classifications:

# def expectedInformationGain(p0,M_ll,M_nn):
# 
#     p1 = update(p0,M_ll,M_nn,1);
#     info1 = mutualInformation(p0,p1);
#     
#     p1 = update(p0,M_ll,M_nn,0);
#     info2 = mutualInformation(p0,p1);
# 
#     return p0*info1 + (1-p0)*info2;
# 
# PJM: I think the above code is wrong: the expectation refers to one
#      to be taken over possible classifications, not truths (we already
#      did that in the information gain function)

def expectedInformationGain(p0, M_ll, M_nn):

    p1 = 1-p0

    I =   p0 * (shannon(M_ll) + shannon(1-M_ll)) \
        + p1 * (shannon(M_nn) + shannon(1-M_nn)) \
        - shannon(M_ll*p0 + (1-M_nn)*p1) \
        - shannon((1-M_ll)*p0 + M_nn*p1)

    return I

# ----------------------------------------------------------------------------
# The information (relative entropy) contributed by an agent, defined by 
# confusion matrix M, having classified a subject, that arrived having 
# probability 'p0', as being 'c' (true/false):

def informationGain(p0, M_ll, M_nn, lens):

    p1 = 1-p0

    if lens:
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

# ----------------------------------------------------------------------------
# Bayesian update of the probability of a subject by an agent whose
# confusion matrix is defined by M

def update(p0,M_ll,M_nn,lens):

#     if(lens):
#         return p0*M_ll/(p0*M_ll+(1.-M_nn)*(1.-p0));
#     else:
#         return p0*(1-M_ll)/(p0*(1-M_ll)+M_nn*(1.-p0));

    if(lens):
        M_cl = M_ll
        M_cn = 1.0 - M_nn
    else:
        M_cl = 1.0 - M_ll
        M_cn = M_nn
    
    return p0*M_cl/(p0*M_cl+(1.0-p0)*M_cn)
    
# PJM: I re-factored this so that the update eqn was in terms of 
#      M_cl and M_cn (to match my notes). 

#============================================================================
# Test plots!
# For some reason these do not work from the swap directory...

if ( __name__ == "__main__"):
    
    # arr=np.reshape(np.array(101*101),(101,101)); 
    # print expGain(0.5,0.3,0.2);
    # print expGain(0.5,0.1,0.4);
    
    import matplotlib.pyplot as plt

    print 'Calculating expected information gain for a volunteer with 0.75 correctness in both classes...'

    # Priors over the classes in a binary classification problem
    logp0 = np.linspace(-4, 0, 500)
    p0 = 10**logp0

    # 2x2 confusion matrices of some volunteers' agents:
    M_ll = [0.55,0.80,0.999,0.25,0.9999,0.500,0.999]
    M_nn = [0.55,0.80,0.999,0.25,0.0001,0.999,0.500]

    almostrandom = expectedInformationGain(p0, M_ll[0], M_nn[0]) 
    mediumastute = expectedInformationGain(p0, M_ll[1], M_nn[1])
    highlyastute = expectedInformationGain(p0, M_ll[2], M_nn[2]) 
    fairlyobtuse = expectedInformationGain(p0, M_ll[3], M_nn[3])
    optimistroll = expectedInformationGain(p0, M_ll[4], M_nn[4])
    slightpessimist = expectedInformationGain(p0, M_ll[5], M_nn[5])
    slightoptimist = expectedInformationGain(p0, M_ll[6], M_nn[6])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(p0, almostrandom, label=("Almost Random: ["+str(M_ll[0])+", "+str(M_nn[0])+"]") )
    ax.plot(p0, mediumastute, label=("Medium Astute: ["+str(M_ll[1])+", "+str(M_nn[1])+"]") )
    ax.plot(p0, highlyastute, label=("Highly Astute: ["+str(M_ll[2])+", "+str(M_nn[2])+"]") )
    ax.plot(p0, fairlyobtuse, label=("Fairly Obtuse: ["+str(M_ll[3])+", "+str(M_nn[3])+"]") )
    ax.plot(p0, optimistroll, label=("Optimist Troll: ["+str(M_ll[4])+", "+str(M_nn[4])+"]") )
    ax.plot(p0, slightpessimist, label=("Slight Pessimist: ["+str(M_ll[5])+", "+str(M_nn[5])+"]") )
    ax.plot(p0, slightoptimist, label=("Slight Optimist: ["+str(M_ll[6])+", "+str(M_nn[6])+"]") )
    ax.axvline(x=0.5, ls=':')
    ax.set_xscale('log')
    ax.set_title("M&M Expected Information Gain")
    ax.set_xlabel("Pr(LENS)")
    ax.set_ylabel("Expected information transmitted by Agent (bits)")
    ax.legend(loc="best")
    #plt.show()
    fig.savefig('MM_expectedinfogain.png')

    print 'Testing the contribution of volunteers after observing a classification'

    almostrandomTrue = informationGain(p0, M_ll[0], M_nn[0], True ) 
    mediumastuteTrue  = informationGain(p0, M_ll[1], M_nn[1], True )
    highlyastuteTrue  = informationGain(p0, M_ll[2], M_nn[2], True ) 
    fairlyobtuseTrue  = informationGain(p0, M_ll[3], M_nn[3], True )
    optimistrollTrue  = informationGain(p0, M_ll[4], M_nn[4], True )
    slightpessimistTrue  = informationGain(p0, M_ll[5], M_nn[5], True )
    slightoptimistTrue  = informationGain(p0, M_ll[6], M_nn[6], True )
    
    almostrandomFalse = informationGain(p0, M_ll[0], M_nn[0], False ) 
    mediumastuteFalse  = informationGain(p0, M_ll[1], M_nn[1], False )
    highlyastuteFalse  = informationGain(p0, M_ll[2], M_nn[2], False ) 
    fairlyobtuseFalse  = informationGain(p0, M_ll[3], M_nn[3], False )
    optimistrollFalse  = informationGain(p0, M_ll[4], M_nn[4], False )
    slightpessimistFalse  = informationGain(p0, M_ll[5], M_nn[5], False )
    slightoptimistFalse  = informationGain(p0, M_ll[6], M_nn[6], False )

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.plot(p0, almostrandomTrue, label=("Almost Random: ["+str(M_ll[0])+", "+str(M_nn[0])+"]") )
    ax.plot(p0, mediumastuteTrue, label=("Medium Astute: ["+str(M_ll[1])+", "+str(M_nn[1])+"]") )
    ax.plot(p0, highlyastuteTrue, label=("Highly Astute: ["+str(M_ll[2])+", "+str(M_nn[2])+"]") )
    ax.plot(p0, fairlyobtuseTrue, label=("Fairly Obtuse: ["+str(M_ll[3])+", "+str(M_nn[3])+"]") )
    ax.plot(p0, optimistrollTrue, label=("Optimist Troll: ["+str(M_ll[4])+", "+str(M_nn[4])+"]") )
    ax.plot(p0, slightpessimistTrue, label=("Slight Pessimist: ["+str(M_ll[5])+", "+str(M_nn[5])+"]") )
    ax.plot(p0, slightoptimistTrue, label=("Slight Optimist: ["+str(M_ll[6])+", "+str(M_nn[6])+"]") )
    ax.axvline(x=0.5, ls=':')    
 
    ax.set_xscale('log')
    ax.set_title("M&M Information Gain when C = True")
    ax.set_xlabel("p(LENS)")
    ax.set_ylabel("Information transmitted by an Agent (bits)")
    ax.legend(loc="best")
    fig.savefig('MM_infogain_true.png')       
 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.plot(p0, almostrandomFalse, label=("Almost Random: ["+str(M_ll[0])+", "+str(M_nn[0])+"]") )
    ax.plot(p0, mediumastuteFalse, label=("Medium Astute: ["+str(M_ll[1])+", "+str(M_nn[1])+"]") )
    ax.plot(p0, highlyastuteFalse, label=("Highly Astute: ["+str(M_ll[2])+", "+str(M_nn[2])+"]") )
    ax.plot(p0, fairlyobtuseFalse, label=("Fairly Obtuse: ["+str(M_ll[3])+", "+str(M_nn[3])+"]") )
    ax.plot(p0, optimistrollFalse, label=("Optimist Troll: ["+str(M_ll[4])+", "+str(M_nn[4])+"]") )
    ax.plot(p0, slightpessimistFalse, label=("Slight Pessimist: ["+str(M_ll[5])+", "+str(M_nn[5])+"]") )
    ax.plot(p0, slightoptimistFalse, label=("Slight Optimist: ["+str(M_ll[6])+", "+str(M_nn[6])+"]") )
    ax.axvline(x=0.5, ls=':')     
    
    #ax.plot(p0, sampleRes, label=("true, M_ll="+str(M_ll[0])+", M_nn="+str(M_nn[0])) )
    #ax.plot(p0, sampleResFalse, label=("false, M_ll="+str(M_ll[0])+", M_nn="+str(M_nn[0])) )
    ax.set_xscale('log')
    ax.set_title("M&M Information Gain when C = False")
    ax.set_xlabel("p(LENS)")
    ax.set_ylabel("Information transmitted by an Agent (bits)")
    ax.legend(loc="best")
    #plt.show()
    fig.savefig('MM_infogain_false.png')
