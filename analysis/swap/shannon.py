#============================================================================
#calculate shannon information

from numpy import log2, ndarray

def shannon(x):
    if isinstance(x, ndarray) == False:
        if x>0:
            return x*log2(x)
        else:
            return 0.0


    x[x == 0] = 1.0
    return x*log2(x)

def expectedInformationGain(p0, M_ll, M_nn):
    p1 = 1-p0

    I = p0 * (shannon(M_ll) + shannon(1-M_ll)) + \
        p1 * (shannon(M_nn) + shannon(1-M_nn)) - \
        shannon(M_ll*p0 + (1-M_nn)*p1) - \
        shannon((1-M_ll)*p0 + M_nn*p1)

    return I

#calculate the information contributed by a user for a given classification
def informationGain(p0, M_ll, M_nn, c):
    p1 = 1-p0

    if c:
        M_cl = M_ll
        M_cn = 1-M_nn
    else:
        M_cl = 1-M_ll
        M_cn = M_nn

    #oldI = -shannon(p0) -shannon(p1) - np.log2(M_cl*p0 + M_cn*p1) \
    #        + (1/(M_cl*p0 + M_cn*p1))*(p0*shannon(M_cl) + M_cl*shannon(p0) \
    #                                 + p1*shannon(M_cn) + M_cn*shannon(p1) )
    #print str(oldI)

    pc = M_cl*p0 + M_cn*p1

    #if isinstance(pc, np.ndarray):
    #    p0_c = pc
    #    p1_c = pc

    #    p0_c[pc!=0] = M_cl/pc[pc!=0]
    #    p1_c[pc!=0] = M_cn/pc[pc!=0]
    #elif pc==0:
    #    p0_c = 0
    #    p1_c = 0
    #else:

    p0_c = M_cl/pc
    p1_c = M_cn/pc

    #print str(p0)
    #print str(p1)
    #print "p0_c=" + str(p0_c*p0) + ", p1_c=" + str(p1_c*p1) + ", total=" + str(p0_c*p0+p1_c*p1)

    I = p0*shannon(p0_c) + p1*shannon(p1_c)

    return I
