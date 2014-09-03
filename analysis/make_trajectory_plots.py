#!/usr/bin/env python
# ======================================================================

import sys,getopt,numpy as np

# import matplotlib
# # Force matplotlib to not use any Xwindows backend:
# matplotlib.use('Agg')
# 
# # Fonts, latex:
# matplotlib.rc('font',**{'family':'serif', 'serif':['TimesNewRoman']})
# matplotlib.rc('text', usetex=True)
# 
# from matplotlib import pyplot as plt
# 
# bfs,sfs = 20,16
# params = { 'axes.labelsize': bfs,
#             'text.fontsize': bfs,
#           'legend.fontsize': bfs,
#           'xtick.labelsize': sfs,
#           'ytick.labelsize': sfs}
# plt.rcParams.update(params)

import swap

# ======================================================================

def make_trajectory_plots(argv):
    """
    NAME
        make_trajectory_plots

    PURPOSE
        Given a collection pickle, this script plots a set of 
        user-specified subject trajectories, possibly against a bacground 
        of random trajectories.

    COMMENTS

    FLAGS
        -h                        Print this message

    INPUTS
        collection.pickle
        
    OPTIONAL INPUTS
        -f list.txt               Plain text list of subject IDs to highlight
        -b --backdrop             Plot 200 random subjects as a backdrop
        -t title                  Title for plot
        --histogram               Include the histogram

    OUTPUTS
        trajectories.png          PNG plot

    EXAMPLE

    BUGS

    AUTHORS
        This file is part of the Space Warps project, and is distributed
        under the GPL v2 by the Space Warps Science Team.
        http://spacewarps.org/

    HISTORY
      2013-09-02  started Marshall (KIPAC)
    """

    # ------------------------------------------------------------------

    try:
       opts, args = getopt.getopt(argv,"hf:bt:",["help","backdrop","histogram"])
    except getopt.GetoptError, err:
       print str(err) # will print something like "option -a not recognized"
       print make_trajectory_plots.__doc__  # will print the big comment above.
       return

    listfile = None
    highlights = False
    backdrop = False
    title = 'Example Subject Trajectories'
    histogram = False

    for o,a in opts:
       if o in ("-h", "--help"):
          print make_trajectory_plots.__doc__
          return
       elif o in ("-f"):
          listfile = a
          highlights = True
       elif o in ("-b", "--backdrop"):
          backdrop = False
       elif o in ("-histogram"):
          histogram = True
       elif o in ("-t"):
          title = a
       else:
          assert False, "unhandled option"
    
    # Check for pickles in array args:
    if len(args) == 1:
        collectionfile = args[0]
        print "make_trajectory_plots: illustrating subject trajectories in: "
        print "make_trajectory_plots: ",collectionfile
    else:
        print make_trajectory_plots.__doc__
        return

    output_directory = './'

    # ------------------------------------------------------------------
    # Read in collection:

    sample = swap.read_pickle(collectionfile, 'collection')
    print "make_trajectory_plots: total no. of available subjects: ",len(sample.list())

    if highlights:
        # Read in subjects to be highlighted:
        highlightIDs = swap.read_list(listfile)
        print highlightIDs
        print "make_trajectory_plots: total no. of special subjects: ",len(highlightIDs)
        print "make_trajectory_plots: special subjects: ",highlightIDs
       
    # ------------------------------------------------------------------

    # Start plot:
    figure = sample.start_trajectory_plot(title=title,histogram=histogram,logscale=False)
    pngfile = 'trajectories.png'

    if backdrop:
        # Plot random 200 trajectories as background:
        Ns = np.min([200,sample.size()])
        print "make_trajectory_plots: plotting "+str(Ns)+" random subject trajectories in "+pngfile
        for ID in sample.shortlist(Ns):
            sample.member[ID].plot_trajectory(figure)

    # Overlay highlights, correctly colored:
    if highlights:
        for ID in highlightIDs:
            sample.member[ID].plot_trajectory(figure,highlight=True)
    
    # Finish off:
    sample.finish_trajectory_plot(figure,pngfile)
    
    # ------------------------------------------------------------------

    print "make_trajectory_plots: all done!"

    return


# ======================================================================

if __name__ == '__main__': 
    make_trajectory_plots(sys.argv[1:])

# ======================================================================
