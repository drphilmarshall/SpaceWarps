#!/usr/bin/env python
# ======================================================================

# from __future__ import division
# from skimage import io
from subprocess import call
# from colors import blues_r

import sys,getopt,numpy as np

import matplotlib
# Force matplotlib to not use any Xwindows backend:
matplotlib.use('Agg')

# Fonts, latex:
matplotlib.rc('font',**{'family':'serif', 'serif':['TimesNewRoman']})
matplotlib.rc('text', usetex=True)

from matplotlib import pyplot as plt

bfs,sfs = 20,16
params = { 'axes.labelsize': bfs,
            'text.fontsize': bfs,
          'legend.fontsize': bfs,
          'xtick.labelsize': sfs,
          'ytick.labelsize': sfs}
plt.rcParams.update(params)

import swap

# ======================================================================

def make_crowd_plots(argv):
    """
    NAME
        make_crowd_plots

    PURPOSE
        Given stage1 and stage2 bureau pickles, this script produces the 
        4 plots currently planned for the crowd section of the SW system 
        paper.

    COMMENTS

    FLAGS
        -h                Print this message

    INPUTS
        --cornerplotter   $CORNERPLOTTER_DIR
        stage1_bureau.pickle
        stage2_bureau.pickle

    OUTPUTS
        Various png plots.

    EXAMPLE

    BUGS
        - Code is not tested yet...

    AUTHORS
        This file is part of the Space Warps project, and is distributed
        under the GPL v2 by the Space Warps Science Team.
        http://spacewarps.org/

    HISTORY
      2013-05-17  started Baumer & Davis (KIPAC)
      2013-05-30  opts, docs Marshall (KIPAC)
    """

    # ------------------------------------------------------------------

    try:
       opts, args = getopt.getopt(argv,"hc",["help","cornerplotter"])
    except getopt.GetoptError, err:
       print str(err) # will print something like "option -a not recognized"
       print make_crowd_plots.__doc__  # will print the big comment above.
       return

    cornerplotter_path = ''
    resurrect = False

    for o,a in opts:
       if o in ("-h", "--help"):
          print make_crowd_plots.__doc__
          return
       elif o in ("-c", "--cornerplotter"):
          cornerplotter_path = a+'/'
       else:
          assert False, "unhandled option"

    # Check for pickles in array args:
    if len(args) == 2:
        bureau1_path = args[0]
        bureau2_path = args[1]
        print "make_crowd_plots: illustrating behaviour captured in bureau files: "
        print "make_crowd_plots: ",bureau1_path
        print "make_crowd_plots: ",bureau2_path
    else:
        print make_crowd_plots.__doc__
        return

    cornerplotter_path = cornerplotter_path+'CornerPlotter.py'
    output_directory = './'

    # ------------------------------------------------------------------

    # Read in bureau objects:

    bureau1 = swap.read_pickle(bureau1_path, 'bureau')
    bureau2 = swap.read_pickle(bureau2_path, 'bureau')
    print "make_crowd_plots: stage 1, 2 agent numbers: ",len(bureau1.list()), len(bureau2.list())

    # make lists by going through agents
    N_early = 10

    stage2_veteran_members = []
    list1 = bureau1.list()
    for ID in bureau2.list():
        if ID in list1:
            stage2_veteran_members.append(ID)
    print "make_crowd_plots: ",len(stage2_veteran_members), " volunteers stayed on for Stage 2 from Stage 1"

    final_skill = []
    contribution = []
    experience = []
    effort = []
    information = []
    early_skill = []
    
    final_skill_all = []
    contribution_all = []
    experience_all = []
    effort_all = []
    information_all = []

    for ID in bureau1.list():
        agent = bureau1.member[ID]
        final_skill_all.append(agent.traininghistory['Skill'][-1])
        information_all.append(agent.testhistory['I'].sum())
        effort_all.append(agent.N-agent.NT)
        experience_all.append(agent.NT)
        contribution_all.append(agent.testhistory['Skill'].sum()) #total integrated skill applied
        if agent.NT < N_early:
            continue

        final_skill.append(agent.traininghistory['Skill'][-1])
        information.append(agent.testhistory['I'].sum())
        effort.append(agent.N-agent.NT)
        experience.append(agent.NT)
        early_skill.append(agent.traininghistory['Skill'][N_early])
        contribution.append(agent.testhistory['Skill'].sum())

    experience = np.array(experience)
    effort = np.array(effort)
    final_skill = np.array(final_skill)
    contribution = np.array(contribution)
    experience_all = np.array(experience_all)
    effort_all = np.array(effort_all)
    final_skill_all = np.array(final_skill_all)
    contribution_all = np.array(contribution_all)
    early_skill = np.array(early_skill)
    contribution = np.array(contribution)
    contribution_all = np.array(contribution_all)


    #same setup for stage 2, except special class is veteran volunteers rather than "experienced" volunteers

    final_skill2 = []
    contribution2 = []
    experience2 = []
    effort2 = []
    information2 = []
    
    final_skill_all2 = []
    contribution_all2 = []
    experience_all2 = []
    effort_all2 = []
    information_all2 = []
    
    new_s2_contribution = []
    new_s2_skill = []
    new_s2_effort = []

    for ID in bureau2.list():
        agent = bureau2.member[ID]
        final_skill_all2.append(agent.traininghistory['Skill'][-1])
        information_all2.append(agent.testhistory['I'].sum())
        effort_all2.append(agent.N-agent.NT)
        experience_all2.append(agent.NT)
        contribution_all2.append(agent.testhistory['Skill'].sum()) #total integrated skill applied
        if agent.name not in stage2_veteran_members:
            new_s2_contribution.append(agent.testhistory['Skill'].sum())
            new_s2_skill.append(agent.traininghistory['Skill'][-1])
            new_s2_effort.append(agent.N-agent.NT)
            continue

        final_skill2.append(agent.traininghistory['Skill'][-1])
        information2.append(agent.testhistory['I'].sum())
        effort2.append(agent.N-agent.NT)
        experience2.append(agent.NT)
        contribution2.append(agent.testhistory['Skill'].sum())

    experience2 = np.array(experience2)
    effort2 = np.array(effort2)
    final_skill2 = np.array(final_skill2)
    contribution2 = np.array(contribution2)
    experience_all2 = np.array(experience_all2)
    effort_all2 = np.array(effort_all2)
    final_skill_all2 = np.array(final_skill_all2)
    contribution_all2 = np.array(contribution_all2)
    contribution2 = np.array(contribution2)
    contribution_all2 = np.array(contribution_all2)
    new_s2_contribution = np.array(new_s2_contribution)
    new_s2_skill = np.array(new_s2_skill)
    new_s2_effort = np.array(new_s2_effort)


    # ------------------------------------------------------------------

    # Plot #1: cumulative distribution of contribution
    plt.figure(figsize=(10,8))

    # All Stage 1 volunteers:
    cumulativecontribution1_all = np.cumsum(np.sort(contribution_all)[::-1])
    totalcontribution1_all = cumulativecontribution1_all[-1]
    Nv1_all = len(cumulativecontribution1_all)
    # Fraction of total contribution, fraction of volunteers:
    cfrac1_all = cumulativecontribution1_all / totalcontribution1_all
    vfrac1_all = np.arange(Nv1_all) / float(Nv1_all)
    plt.plot(vfrac1_all, cfrac1_all, '-b', linewidth=4, label='CFHTLS Stage 1: All Volunteers')
    print "make_crowd_plots: ",Nv1_all,"stage 1 volunteers contributed",phr(totalcontribution1_all),"bits of information"
    index = np.where(cfrac1_all > 0.9)[0][0]
    print "make_crowd_plots: ",phr(100*vfrac1_all[index]),"% of the volunteers -",int(Nv1_all*vfrac1_all[index]),"people - contributed 90% of the information at Stage 1"

    # Experienced Stage 1 volunteers (normalize to all!):
    cumulativecontribution1 = np.cumsum(np.sort(contribution)[::-1])
    totalcontribution1 = cumulativecontribution1[-1]
    Nv1 = len(cumulativecontribution1)
    # Fraction of total contribution (from experienced volunteers), fraction of (experienced) volunteers:
    cfrac1 = cumulativecontribution1 / totalcontribution1_all
    vfrac1 = np.arange(Nv1) / float(Nv1)
    plt.plot(vfrac1, cfrac1, '--b', linewidth=4, label='CFHTLS Stage 1: Experienced Volunteers')
    print "make_crowd_plots: ",Nv1,"experienced stage 1 volunteers contributed",phr(totalcontribution1),"bits of information"
    index = np.where(cfrac1 > 0.9)[0][0]
    print "make_crowd_plots: ",phr(100*vfrac1[index]),"% of the experienced volunteers -",int(Nv1*vfrac1[index]),"people - contributed 90% of the information at Stage 1"

    # All Stage 2 volunteers:
    cumulativecontribution2_all = np.cumsum(np.sort(contribution_all2)[::-1])
    totalcontribution2_all = cumulativecontribution2_all[-1]
    Nv2_all = len(cumulativecontribution2_all)
    # Fraction of total contribution, fraction of volunteers:
    cfrac2_all = cumulativecontribution2_all / totalcontribution2_all
    vfrac2_all = np.arange(Nv2_all) / float(Nv2_all)
    plt.plot(vfrac2_all, cfrac2_all, '#FF8000', linewidth=4, label='CFHTLS Stage 2: All Volunteers')
    print "make_crowd_plots: ",Nv2_all,"stage 2 volunteers contributed",phr(totalcontribution2_all),"bits of information"
    index = np.where(cfrac2_all > 0.9)[0][0]
    print "make_crowd_plots: ",phr(100*vfrac2_all[index]),"% of the volunteers -",int(Nv2_all*vfrac2_all[index]),"people - contributed 90% of the information at Stage 2"

    plt.xlabel('Fraction of Volunteers')
    plt.ylabel('Fraction of Total Contribution')
    plt.xlim(0.0, 0.21)
    plt.ylim(0.0, 1.0)
    plt.legend(loc='lower right')
    pngfile = output_directory+'crowd_contrib_cumul.png'
    plt.savefig(pngfile, bbox_inches='tight')
    print "make_crowd_plots: cumulative contribution plot saved to "+pngfile


    # ------------------------------------------------------------------
    # Plot 1.5: skill histograms? linear x axis, logarithmic y?


    # ------------------------------------------------------------------

    # Plot #2: is final skill predicted by early skill?

    plt.figure(figsize=(10,8))
    plt.xlim(-0.02,0.25)
    plt.ylim(-0.02,0.8)
    plt.xlabel('Early Skill, $\langle I \\rangle_{j<10}$ / bits')
    plt.ylabel('Final Skill, $\langle I \\rangle_{j=N_{\\rm T}}$ / bits')
    size = 400.0
    plt.scatter(early_skill,final_skill,s=size,color='blue',alpha=0.05)
    pngfile = output_directory+'early_vs_final_skill.png'
    plt.savefig(pngfile, bbox_inches='tight')
    print "make_crowd_plots: skill-skill plot saved to "+pngfile

    # ------------------------------------------------------------------

    # Plot #3: corner plot for 5 variables of interest; stage1 = blue shaded, stage2 = orange outlines.

    X = np.vstack((final_skill_all, effort_all, contribution_all, information_all, experience_all)).T

    pos_filter = True
    for Xi in X.T:
        pos_filter *= Xi > 0
    pos_filter *= final_skill_all > 1e-7
    pos_filter *= contribution_all > 1e-11
    X = np.log10(X[pos_filter])

    comment = 'log(Skill), log(Effort), log(Contribution), log(Information), log(Experience)\n{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}'.format(X[:, 0].min(), X[:, 0].max(),
                                                                                                                                    X[:, 1].min(), X[:, 1].max(),
                                                                                                                                    X[:, 2].min(), X[:, 2].max(),
                                                                                                                                    X[:, 3].min(), X[:, 3].max(),
                                                                                                                                    X[:, 4].min(), X[:, 4].max(),)
#     comment = 'Final Skill, Effort, Contribution, Information, Experience\n{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}'.format(X[:, 0].min(), X[:, 0].max(),
#                                                                                                                                     X[:, 1].min(), X[:, 1].max(),
#                                                                                                                                     X[:, 2].min(), X[:, 2].max(),
#                                                                                                                                     X[:, 3].min(), X[:, 3].max(),
#                                                                                                                                     X[:, 4].min(), X[:, 4].max(),)
#     comment = '$\log_{10}$ Skill, $\log_{10}$ Effort, $\log_{10}$ Contribution, $\log_{10}{\sum_k I_k}$, $\log_{10}$ Experience\n{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}'.format(
#                                                                                                                                                                                           X[:, 0].min(), X[:, 0].max(),  
#                                                                                                                                                                                           X[:, 1].min(), X[:, 1].max(),  
#                                                                                                                                                                                           X[:, 2].min(), X[:, 2].max(),  
#                                                                                                                                                                                           X[:, 3].min(), X[:, 3].max(),  
#                                                                                                                                                                                           X[:, 4].min(), X[:, 4].max(),) 
    np.savetxt(output_directory+'volunteer_analysis1.cpt', X, header=comment)

    X = np.vstack((final_skill_all2, effort_all2, contribution_all2, information_all2, experience_all2)).T

    pos_filter = True
    for Xi in X.T:
        pos_filter *= Xi > 0
    pos_filter *= final_skill_all2 > 1e-7
    pos_filter *= contribution_all2 > 1e-11
    X = np.log10(X[pos_filter])

    np.savetxt(output_directory+'volunteer_analysis2.cpt', X, header=comment)

    pngfile = output_directory+'all_skill_contribution_experience_education.png'
    input1 = output_directory+'volunteer_analysis1.cpt,blue,shaded'
    input2 = output_directory+'volunteer_analysis2.cpt,orange,shaded'

    call([cornerplotter_path,'-o',pngfile,input1,input2])

    print "make_crowd_plots: corner plot saved to "+pngfile

    # ------------------------------------------------------------------

    # Plot #4: stage 2 -- new volunteers vs. veterans: contribution.

    plt.figure(figsize=(10,8))
    plt.xlim(-10.0,895.0)
    plt.ylim(-0.02,0.85)
    plt.xlabel('Stage 2 Contribution $\sum_k \langle I \\rangle_k$ / bits')
    plt.ylabel('Stage 2 Skill $\langle I \\rangle_{j=N_{\\rm T}}$ / bits')

    size = 0.5*effort2
    plt.scatter(contribution2, final_skill2, s=size, color='blue', alpha=0.4)
    plt.scatter(contribution2, final_skill2,         color='blue', alpha=0.4, label='Veteran volunteers from Stage 1')
    size = 0.5*new_s2_effort
    plt.scatter(new_s2_contribution, new_s2_skill,s = size, color='#FFA500', alpha=0.4)
    plt.scatter(new_s2_contribution, new_s2_skill,          color='#FFA500', alpha=0.4, label='New Stage 2 volunteers')

    Nvets = len(contribution2)
    Nnewb = len(new_s2_contribution)
    N = Nvets + Nnewb
    totalvets = np.sum(contribution2)
    totalnewb = np.sum(new_s2_contribution)
    total = totalvets + totalnewb
    print "make_crowd_plots: total contribution in Stage 2 was",phr(total),"bits by",N,"volunteers"

    x0,y0,z0 = np.mean(contribution2),np.mean(final_skill2),np.mean(effort2)
    l = plt.axvline(x=x0,color='blue',ls='--')
    l = plt.axhline(y=y0,color='blue',ls='--')
    print "make_crowd_plots: ",Nvets,"veteran users (",phr(100*Nvets/N),"% of the total) made",phr(100*totalvets/total),"% of the contribution"
    print "make_crowd_plots: the average stage 2 veteran had skill, contribution, effort = ",phr(y0,ndp=2),phr(x0),int(z0)
    
    x0,y0,z0 = np.mean(new_s2_contribution),np.mean(new_s2_skill),np.mean(new_s2_effort)
    l = plt.axvline(x=x0,color='#FFA500',ls='--')
    l = plt.axhline(y=y0,color='#FFA500',ls='--')
    print "make_crowd_plots: ",Nnewb,"new users (",phr(100*Nnewb/N),"% of the total) made",phr(100*totalnewb/total),"% of the contribution"
    print "make_crowd_plots: the average stage 2 newbie had skill, contribution, effort = ",phr(y0,ndp=2),phr(x0),int(z0)

    plt.legend(loc='upper right')
    pngfile = output_directory+'stage2_veteran_contribution.png'
    plt.savefig(pngfile, bbox_inches='tight')
    print "make_crowd_plots: newbies vs veterans plot saved to "+pngfile

    # ------------------------------------------------------------------

    print "make_crowd_plots: all done!"

    return

# ======================================================================

def phr(x,ndp=1):
    fmt = "%d" % ndp
    fmt = '%.'+fmt+'f'
    return fmt % x

# ======================================================================

if __name__ == '__main__': 
    make_crowd_plots(sys.argv[1:])

# ======================================================================
