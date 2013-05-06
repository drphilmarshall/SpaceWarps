# ===========================================================================

import swap

import subprocess,sys,os,time
import numpy as np

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

# ======================================================================
# Write a PDF report, using latex:

def write_report(pars,crowd,sample):

    tex = pars['stem']+'_report.tex'

    print "SWAP: writing report in "+tex

    # Get started:
    F = open(tex,"w")
    swap.write_report_preamble(F)

    # Top left panel holds a summary of numbers:
    
    F.write('\\begin{minipage}{0.42\linewidth}\n')

    title = pars['survey'].replace('_',',')

    F.write('{\LARGE %s}\\newline\n' % title)
    F.write('\medskip\n\n')
    
    F.write('\\begin{tabular}{|p{0.65\linewidth}p{0.2\linewidth}|}\n')
    F.write('\hline\n')
    F.write('Number of classifications:         & %d   \\\\ \n' % (np.sum(sample.exposure['sim'])+np.sum(sample.exposure['dud'])+np.sum(sample.exposure['test'])))
    F.write('Number of classifiers:             & %d   \\\\ \n' % len(crowd.member))
    F.write('Number of subjects:                & %d   \\\\ \n' % len(sample.member))
    F.write('Number of sims:                    & %d   \\\\ \n' % len(sample.probabilities['sim']))
    F.write('Number of duds:                    & %d   \\\\ \n' % len(sample.probabilities['dud']))
    F.write('\hline\n')
    F.write('\end{tabular}\n')

    F.write('\\begin{tabular}{|p{0.65\linewidth}p{0.2\linewidth}|}\n')
    F.write('\hline\n')
    F.write('Mean test class$^{\\rm n}$s/classifier: & %.1f \\\\ \n' % (np.average(crowd.Ntest)))
    F.write('Mean class$^{\\rm n}$s/test subject:    & %.1f \\\\ \n' % (np.average(sample.exposure['test'])))
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

#=======================================================================

if __name__ == '__main__':

    pass
    
#=======================================================================
