# ===========================================================================

import swap

import subprocess,sys,os,time
import numpy as np
from subject import Ntrajectory

# ======================================================================

"""
    NAME
        logging.py

    PURPOSE
        Bits and pieces to help make a nice output log.
        
    COMMENTS
        Based on https://github.com/drphilmarshall/Pangloss/blob/master/pangloss/miscellaneous.py
        
    FUNCTIONS
        
    BUGS

    AUTHORS
      This file is part of the Space Warps project, and is distributed 
      under the GPL v2 by the Space Warps Science Team.
      http://spacewarps.org/

    HISTORY
      2013-04-17  Started: Marshall (Oxford)
"""

# =========================================================================

dashedline       = 'SWAP: --------------------------------------------------------------------------'
doubledashedline = '================================================================================'

hello            = '                   SWAP: the Space Warps Analysis Pipeline                      '
helloswitch      = '                   SWITCH: the Space Warps Retirement Plan                      '

# ======================================================================
# Write a PDF report, using latex:

def write_report(pars,bureau,sample):

    tex = pars['dir']+'/'+pars['trunk']+'_report.tex'

    print "SWAP: writing report in "+tex

    # Get started:
    F = open(tex,"w")
    swap.write_report_preamble(F)

    # Top left panel holds a summary of numbers.
    
    F.write('\\begin{minipage}{0.42\linewidth}\n')

    title = pars['survey'].replace('_',',')

    F.write('{\LARGE %s}\\newline\n' % title)
    F.write('\medskip\n\n')
    
    # First, just count things:

    sample.take_stock()
    
    bureau.collect_probabilities()
    
    Nmade = np.sum(bureau.Ntotal)
    Nused = np.sum(sample.exposure['sim'])+np.sum(sample.exposure['dud'])+np.sum(sample.exposure['test'])    
    Nc = len(bureau.member)
    
    # Ns = len(sample.member)
    # assert (Ns == sample.N)
    Ns = sample.Ns

    Ntl = len(sample.probabilities['sim'])
    assert (Ntl == sample.Ntl)

    Ntd = len(sample.probabilities['dud'])
    assert (Ntd == sample.Ntd)

    F.write('\\begin{tabular}{|p{0.65\linewidth}p{0.2\linewidth}|}\n')
    F.write('\hline\n')
    F.write('Number of classifications:         & %d   \\\\ \n' % Nmade )
    F.write('Number of class$^{\\rm n}$s used:  & %d   \\\\ \n' % Nused )
    F.write('Number of classifiers:             & %d   \\\\ \n' % Nc )
    F.write('Number of test subjects:           & %d   \\\\ \n' % Ns )
    F.write('Number of sims:                    & %d   \\\\ \n' % Ntl )
    F.write('Number of duds:                    & %d   \\\\ \n' % Ntd )
    F.write('\hline\n')
    F.write('\end{tabular}\n')

    # Now, what has the crowd achieved?
    
    Nc_per_classifier = np.average(bureau.Ntest)
    Nc_per_subject    = np.average(sample.exposure['test'])
    Ns_retired = sample.Ns_retired
    Nc_per_retirement = np.average(sample.retirement_ages)
    Ns_rejected = sample.Ns_rejected
    Ns_detected = sample.Ns_detected

    F.write('\\begin{tabular}{|p{0.65\linewidth}p{0.2\linewidth}|}\n')
    F.write('\hline\n')
    F.write('Mean test class$^{\\rm n}$s/classifier: & %.1f \\\\ \n' % Nc_per_classifier )
    F.write('Mean class$^{\\rm n}$s/test subject:    & %.1f \\\\ \n' % Nc_per_subject )
    F.write('Test subject retirements:               & %d   \\\\ \n' % Ns_retired )
    F.write('Mean class$^{\\rm n}$s/retirement:      & %.1f \\\\ \n' % Nc_per_retirement )
    F.write('Test subject rejections:                & %d   \\\\ \n' % Ns_rejected )
    F.write('Test subject identifications:           & %d   \\\\ \n' % Ns_detected )
    F.write('\hline\n')
    F.write('\end{tabular}\n')

    # How complete/pure is the sample likely to be, based on the
    # training set? First, completeness - lenses out over lenses in:
    C_LENS = 100.0*sample.Ntl_detected/(sample.Ntl + (sample.Ntl == 0))
    C_NOT = 100.0*sample.Ntd_rejected/(sample.Ntd + (sample.Ntd == 0))
    
    # Now purity - lenses out over all output:
    P_LENS = 100.0*sample.Ntl_detected/(sample.Nt_detected + (sample.Nt_detected == 0))
    P_NOT = 100.0*sample.Ntd_rejected/(sample.Nt_rejected + (sample.Nt_rejected == 0))

    # False positive contamination - detected duds as fraction of 
    # total detections:
    FP = 100.0*sample.Ntd_detected/(sample.Nt_detected + (sample.Nt_detected == 0))
    # Lenses lost as false negatives - rejected sims as fraction of 
    # total number of input sims:
    FN = 100.0*sample.Ntl_rejected/(sample.Ntl + (sample.Ntl == 0))

    F.write('\\begin{tabular}{|p{0.65\linewidth}p{0.2\linewidth}|}\n')
    F.write('\hline\n')
    F.write('Lens completeness:         & %.1f%s \\\\ \n' % (C_LENS,'\%') )
    F.write('Lens purity:               & %.1f%s \\\\ \n' % (P_LENS,'\%') )
    F.write('Non-lens completeness:     & %.1f%s \\\\ \n' % (C_NOT,'\%')  )
    # F.write('Non-lens purity:           & %.1f%s \\\\ \n' % (P_NOT,'\%')  )
    F.write('Contamination:             & %.1f%s \\\\ \n' % (FP,'\%')  )
    F.write('Lenses missed:             & %.1f%s \\\\ \n' % (FN,'\%')  )
    F.write('\hline\n')
    F.write('\end{tabular}\n')


    F.write('\end{minipage}\hfill\n')
    
    # Other panels contain figures:
    
    swap.add_report_figures(F,pars)

    # Finish off the texfile:
    swap.write_report_ending(F)
    F.close()

    # Compile the pdf:
    
    swap.compile_report(tex,pars)

    return

# ----------------------------------------------------------------------

def write_report_preamble(F):

    F.write('\documentclass[letterpaper,12pt]{article}\n')
    F.write('\usepackage{helvet,mathpple}\n')
    F.write('\usepackage{graphicx}\n')
    F.write('\\renewcommand{\\familydefault}{\sfdefault}\n')
    F.write('\\renewcommand{\\arraystretch}{1.5}\n')
    F.write('\setlength{\oddsidemargin}{-0.65in}\n')
    F.write('\setlength{\\textwidth}{7.75in}\n')
    F.write('\setlength{\\topmargin}{-1.5in}\n')
    F.write('\setlength{\\textheight}{10.5in}\n')
    F.write('\pagestyle{empty}\n')
    F.write('\\begin{document}\n')

    return

# ----------------------------------------------------------------------

def add_report_figures(F,pars):

    # Top Right: Subject trajectories:
    F.write('\\begin{minipage}{0.56\linewidth}\n')
    F.write('\includegraphics[width=\linewidth]{%s}\n' % pars['trajectoriesplot'])
    F.write('\end{minipage}\n\n')

    F.write('\\vspace{-1\\baselineskip}\n')
    F.write('\\begin{minipage}{\linewidth}\n')

    # Bottom Left: Classifier probabilities:
    F.write('\\begin{minipage}{0.48\linewidth}\n')
    F.write('\includegraphics[width=\linewidth]{%s}\n' % pars['probabilitiesplot'])
    F.write('\end{minipage}\n')

    # Bottom Right: Classifier histories:
    F.write('\\begin{minipage}{0.48\linewidth}\n')
    F.write('\includegraphics[width=\linewidth]{%s}\n' % pars['historiesplot'])
    F.write('\end{minipage}\n')
    
    F.write('\end{minipage}\n')

    return
    
# ----------------------------------------------------------------------

def write_report_ending(F):

    F.write('\end{document}\n')

    return

# ----------------------------------------------------------------------

def compile_report(tex,pars):

    stem = tex.split('.')[0]
    pdf = stem+'.pdf'

    # Remove PDF file:
    swap.rm(pdf)

    # Keep a record of what happens:
    log = stem+'.texlog'
    L = open(log,"w")
    
    # Run pdflatex:
    P = subprocess.Popen(["pdflatex",tex],cwd=pars['dir'],stdout=L,stderr=L)
    
    # Wait for it to finish:
    for t in range(10):
        time.sleep(1)
        if P.poll() is not None: continue
    
    # If pdflatex has not finished - kill it.
    if P.poll() is None: P.terminate()
    
    L.close()    
    
    # Check the PDF got made:
    
    if os.path.exists(pdf): 
        print "SWAP: report compiled as "+pdf
    else:
        print "SWAP: pdflatex failed, here's the end of the report:"
        subprocess.call(["tail",log])
        print "SWAP: this report is stored in ",log
        print "SWAP: exiting."
        sys.exit()

    return

# ----------------------------------------------------------------------

def set_cookie(go):
    
    F = open('.swap.cookie','w')
    if go:
        F.write('running')
    else:
        F.write('stopped')
    F.close()

    return

#=======================================================================

if __name__ == '__main__':

    pass
    
#=======================================================================
