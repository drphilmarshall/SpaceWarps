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
        under the MIT license by the Space Warps Science Team.
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

    print "make_crowd_plots: mean stage 1 volunteer effort = ",phr(np.mean(effort_all))
    print "make_crowd_plots: mean stage 1 volunteer experience = ",phr(np.mean(experience_all))
    print "make_crowd_plots: mean stage 1 volunteer contribution = ",phr(np.mean(contribution_all)),"bits"
    print "make_crowd_plots: mean stage 1 volunteer skill = ",phr(np.mean(final_skill_all),ndp=2),"bits"

    #same setup for stage 2, except special class is veteran volunteers rather than "experienced" volunteers

    final_skill2 = []
    contribution2 = []
    experience2 = []
    effort2 = []
    information2 = []
    
    # stage 1 skill of stage 2 classifiers:
    final_skill1 = []
    
    final_skill_all2 = []
    contribution_all2 = []
    experience_all2 = []
    effort_all2 = []
    information_all2 = []
    
    new_s2_contribution = []
    new_s2_skill = []
    new_s2_effort = []
    new_s2_information = []

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
            new_s2_information.append(agent.testhistory['I'].sum())
            continue

        contribution2.append(agent.testhistory['Skill'].sum())
        final_skill2.append(agent.traininghistory['Skill'][-1])
        effort2.append(agent.N-agent.NT)
        information2.append(agent.testhistory['I'].sum())
        experience2.append(agent.NT)

        oldagent = bureau1.member[ID]
        final_skill1.append(oldagent.traininghistory['Skill'][-1])
        

    experience2 = np.array(experience2)
    effort2 = np.array(effort2)
    final_skill2 = np.array(final_skill2)
    contribution2 = np.array(contribution2)
    information2 = np.array(information2)

    experience_all2 = np.array(experience_all2)
    effort_all2 = np.array(effort_all2)
    final_skill_all2 = np.array(final_skill_all2)
    contribution_all2 = np.array(contribution_all2)
    information_all2 = np.array(information_all2)

    new_s2_contribution = np.array(new_s2_contribution)
    new_s2_skill = np.array(new_s2_skill)
    new_s2_effort = np.array(new_s2_effort)
    new_s2_information = np.array(new_s2_information)

    print "make_crowd_plots: mean stage 2 volunteer effort = ",phr(np.mean(effort_all2))
    print "make_crowd_plots: mean stage 2 volunteer experience = ",phr(np.mean(experience_all2))
    print "make_crowd_plots: mean stage 2 volunteer contribution = ",phr(np.mean(contribution_all2)),"bits"
    print "make_crowd_plots: mean stage 2 volunteer skill = ",phr(np.mean(final_skill_all2),ndp=2),"bits"

    # ------------------------------------------------------------------

    # Plot 1.1 and 1.2: cumulative distributions of contribution and skill
    
    # 1.1 Contribution
    
    plt.figure(figsize=(10,8))

    # All Stage 1 volunteers:
    cumulativecontribution1_all = np.cumsum(np.sort(contribution_all)[::-1])
    totalcontribution1_all = cumulativecontribution1_all[-1]
    Nv1_all = len(cumulativecontribution1_all)
    # Fraction of total contribution, fraction of volunteers:
    cfrac1_all = cumulativecontribution1_all / totalcontribution1_all
    vfrac1_all = np.arange(Nv1_all) / float(Nv1_all)
    plt.plot(vfrac1_all, cfrac1_all, '-b', linewidth=4, label='CFHTLS Stage 1: All Volunteers')
    print "make_crowd_plots: ",Nv1_all,"stage 1 volunteers contributed",phr(totalcontribution1_all),"bits"
    index = np.where(cfrac1_all > 0.9)[0][0]
    print "make_crowd_plots: ",phr(100*vfrac1_all[index]),"% of the volunteers -",int(Nv1_all*vfrac1_all[index]),"people - contributed 90% of the information at Stage 1"

    print "make_crowd_plots: total amount of information generated at stage 1 = ",phr(np.sum(information_all)),"bits"

    # Experienced Stage 1 volunteers (normalize to all!):
    cumulativecontribution1 = np.cumsum(np.sort(contribution)[::-1])
    totalcontribution1 = cumulativecontribution1[-1]
    Nv1 = len(cumulativecontribution1)
    # Fraction of total contribution (from experienced volunteers), fraction of (experienced) volunteers:
    cfrac1 = cumulativecontribution1 / totalcontribution1_all
    vfrac1 = np.arange(Nv1) / float(Nv1)
    plt.plot(vfrac1, cfrac1, '--b', linewidth=4, label='CFHTLS Stage 1: Experienced Volunteers')
    print "make_crowd_plots: ",Nv1,"experienced stage 1 volunteers contributed",phr(totalcontribution1),"bits"
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
    print "make_crowd_plots: ",Nv2_all,"stage 2 volunteers contributed",phr(totalcontribution2_all),"bits"
    index = np.where(cfrac2_all > 0.9)[0][0]
    print "make_crowd_plots: ",phr(100*vfrac2_all[index]),"% of the volunteers -",int(Nv2_all*vfrac2_all[index]),"people - contributed 90% of the information at Stage 2"

    print "make_crowd_plots: total amount of information generated at stage 2 = ",phr(np.sum(information_all2)),"bits"

    plt.xlabel('Fraction of Volunteers')
    plt.ylabel('Fraction of Total Contribution')
    plt.xlim(0.0, 0.21)
    plt.ylim(0.0, 1.0)
    plt.legend(loc='lower right')
    pngfile = output_directory+'crowd_contrib_cumul.png'
    plt.savefig(pngfile, bbox_inches='tight')
    print "make_crowd_plots: cumulative contribution plot saved to "+pngfile


    # 1.2 Skill
    
    plt.figure(figsize=(10,8))

    # All Stage 1 volunteers:
    cumulativeskill1_all = np.cumsum(np.sort(final_skill_all)[::-1])
    totalskill1_all = cumulativeskill1_all[-1]
    Nv1_all = len(cumulativeskill1_all)
    # Fraction of total skill, fraction of volunteers:
    cfrac1_all = cumulativeskill1_all / totalskill1_all
    vfrac1_all = np.arange(Nv1_all) / float(Nv1_all)
    plt.plot(vfrac1_all, cfrac1_all, '-b', linewidth=4, label='CFHTLS Stage 1: All Volunteers')
    print "make_crowd_plots: ",Nv1_all,"stage 1 volunteers possess",phr(totalskill1_all),"bits worth of skill"
    index = np.where(vfrac1_all > 0.2)[0][0]
    print "make_crowd_plots: ",phr(100*cfrac1_all[index]),"% of the skill possessed by the (20%) most skilled",int(Nv1_all*vfrac1_all[index]),"people"

    # Experienced Stage 1 volunteers (normalize to all!):
    cumulativeskill1 = np.cumsum(np.sort(final_skill)[::-1])
    totalskill1 = cumulativeskill1[-1]
    Nv1 = len(cumulativeskill1)
    # Fraction of total skill (from experienced volunteers), fraction of (experienced) volunteers:
    cfrac1 = cumulativeskill1 / totalskill1_all
    vfrac1 = np.arange(Nv1) / float(Nv1)
    plt.plot(vfrac1, cfrac1, '--b', linewidth=4, label='CFHTLS Stage 1: Experienced Volunteers')
    print "make_crowd_plots: ",Nv1,"experienced stage 1 volunteers possess",phr(totalskill1),"bits worth of skill"
    index = np.where(vfrac1 > 0.2)[0][0]
    print "make_crowd_plots: ",phr(100*cfrac1[index]),"% of the skill possessed by the (20%) most skilled",int(Nv1*vfrac1[index]),"people"

    # All Stage 2 volunteers:
    cumulativeskill2_all = np.cumsum(np.sort(final_skill_all2)[::-1])
    totalskill2_all = cumulativeskill2_all[-1]
    Nv2_all = len(cumulativeskill2_all)
    # Fraction of total skill, fraction of volunteers:
    cfrac2_all = cumulativeskill2_all / totalskill2_all
    vfrac2_all = np.arange(Nv2_all) / float(Nv2_all)
    plt.plot(vfrac2_all, cfrac2_all, '#FF8000', linewidth=4, label='CFHTLS Stage 2: All Volunteers')
    print "make_crowd_plots: ",Nv2_all,"stage 2 volunteers possess",phr(totalskill2_all),"bits worth of skill"
    index = np.where(vfrac2_all > 0.2)[0][0]
    print "make_crowd_plots: ",phr(100*cfrac2_all[index]),"% of the skill possessed by the (20%) most skilled",int(Nv2_all*vfrac2_all[index]),"people"

    plt.xlabel('Fraction of Volunteers')
    plt.ylabel('Fraction of Total Skill')
    plt.xlim(0.0, 0.21)
    plt.ylim(0.0, 1.0)
    plt.legend(loc='upper left')
    pngfile = output_directory+'crowd_skill_cumul.png'
    plt.savefig(pngfile, bbox_inches='tight')
    print "make_crowd_plots: cumulative skill plot saved to "+pngfile


    # ------------------------------------------------------------------

    # Plot #2: is final skill predicted by early skill?

    N = len(final_skill)
    prodigies_final_skill = final_skill[np.where(early_skill > 0.1)]
    Nprodigies = len(prodigies_final_skill)
    mean_prodigies_skill = np.mean(prodigies_final_skill)
    Ngood_prodigies = len(np.where(prodigies_final_skill > 0.05)[0])
    print "make_crowd_plots: the",Nprodigies,"-",phr(100*Nprodigies/N),"% - of experienced stage 1 volunteers who have early skill > 0.1 go on to attain a mean final skill of",phr(mean_prodigies_skill,ndp=2)
    print "make_crowd_plots: with",phr(100*Ngood_prodigies/Nprodigies),"% of them remaining at skill 0.05 or higher"

    plt.figure(figsize=(10,8))
    plt.xlim(-0.02,0.25)
    plt.ylim(-0.02,0.8)
    plt.xlabel('Early Skill, $\langle I \\rangle_{j<10}$ / bits')
    plt.ylabel('Final Skill, $\langle I \\rangle_{j=N_{\\rm T}}$ / bits')
    # Point size prop to contribution!
    # size = 400.0
    size = 20 + 0.01*contribution
    plt.scatter(early_skill,final_skill,s=size,color='blue',alpha=0.4)
    plt.plot((0.1, 0.1), (0.05, 0.8),color='black',ls='--')
    plt.plot((0.1, 0.25), (0.05, 0.05),color='black',ls='--')
    pngfile = output_directory+'early_vs_final_skill.png'
    plt.savefig(pngfile, bbox_inches='tight')
    print "make_crowd_plots: skill-skill plot saved to "+pngfile

    # ------------------------------------------------------------------

    # Plot #3: corner plot for 5 variables of interest; stage1 = blue shaded, stage2 = orange outlines.

    X = np.vstack((effort_all, experience_all, final_skill_all, contribution_all, information_all)).T

    pos_filter = True
    for Xi in X.T:
        pos_filter *= Xi > 0
    pos_filter *= final_skill_all > 1e-7
    pos_filter *= contribution_all > 1e-11
    X = np.log10(X[pos_filter])

    comment = 'log(Effort), log(Experience),log(Skill), log(Contribution), log(Information)\n{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}'.format(X[:, 0].min(), X[:, 0].max(),
                                                                                                                                    X[:, 1].min(), X[:, 1].max(),
                                                                                                                                    X[:, 2].min(), X[:, 2].max(),
                                                                                                                                    X[:, 3].min(), X[:, 3].max(),
                                                                                                                                    X[:, 4].min(), X[:, 4].max(),)
    np.savetxt(output_directory+'volunteer_analysis1.cpt', X, header=comment)

    X = np.vstack((effort_all2, experience_all2, final_skill_all2, contribution_all2, information_all2)).T

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

    # PJM: updated 2014-09-03 to show stage 1 vs 2 skill, point size shows effort.

    # plt.figure(figsize=(10,8))
    plt.figure(figsize=(8,8))
    # plt.xlim(-10.0,895.0)
    plt.xlim(-0.02,0.85)
    plt.ylim(-0.02,0.85)
    # plt.xlabel('Stage 2 Contribution $\sum_k \langle I \\rangle_k$ / bits')
    plt.xlabel('Stage 1 Skill $\langle I \\rangle_{j=N_{\\rm T}}$ / bits')
    plt.ylabel('Stage 2 Skill $\langle I \\rangle_{j=N_{\\rm T}}$ / bits')

    size = 0.5*effort2
    # size = 20 + 10*information2
    # size = 20 + 10*contribution2
    # plt.scatter(contribution2, final_skill2, s=size, color='blue', alpha=0.4)
    # plt.scatter(contribution2, final_skill2,         color='blue', alpha=0.4, label='Veteran volunteers from Stage 1')
    plt.scatter(final_skill1, final_skill2, s=size, color='blue', alpha=0.4, label='Veteran volunteers from Stage 1')
    # plt.scatter(final_skill1, final_skill2,         color='blue', alpha=0.4, label='Veteran volunteers from Stage 1')
    
    size = 0.5*new_s2_effort
    # size = 20 + 10*new_s2_information
    # size = 20 + 10*new_s2_contribution
    # plt.scatter(new_s2_contribution, new_s2_skill,s = size, color='#FFA500', alpha=0.4)
    # plt.scatter(new_s2_contribution, new_s2_skill,          color='#FFA500', alpha=0.4, label='New Stage 2 volunteers')
    new_s1_skill = new_s2_skill.copy()*0.0 # All had zero skill at stage 1, because they didn't show up!
    plt.scatter(new_s1_skill, new_s2_skill,s = size, color='#FFA500', alpha=0.4, label='New Stage 2 volunteers')
    # plt.scatter(new_s1_skill, new_s2_skill,          color='#FFA500', alpha=0.4, label='New Stage 2 volunteers')

    Nvets = len(contribution2)
    Nnewb = len(new_s2_contribution)
    N = Nvets + Nnewb
    totalvets = np.sum(contribution2)
    totalnewb = np.sum(new_s2_contribution)
    total = totalvets + totalnewb
    print "make_crowd_plots: total contribution in Stage 2 was",phr(total),"bits by",N,"volunteers"

    x0,y0,w0,z0 = np.mean(final_skill1),np.mean(final_skill2),np.mean(contribution2),np.mean(effort2)
    l = plt.axvline(x=x0,color='blue',ls='--')
    l = plt.axhline(y=y0,color='blue',ls='--')
    print "make_crowd_plots: ",Nvets,"stage 1 veteran users (",phr(100*Nvets/N),"% of the total) made",phr(100*totalvets/total),"% of the contribution"
    print "make_crowd_plots: the average stage 1 veteran had skill1, skill2, contribution, effort = ",phr(x0,ndp=2),phr(y0,ndp=2),phr(w0),int(z0)
    
    x0,y0,w0,z0 = np.mean(new_s1_skill),np.mean(new_s2_skill),np.mean(new_s2_contribution),np.mean(new_s2_effort)
    l = plt.axvline(x=x0,color='#FFA500',ls='--')
    l = plt.axhline(y=y0,color='#FFA500',ls='--')
    print "make_crowd_plots: ",Nnewb,"new users (",phr(100*Nnewb/N),"% of the total) made",phr(100*totalnewb/total),"% of the contribution"
    print "make_crowd_plots: the average stage 2 newbie had skill1, skill2, contribution, effort = ",phr(x0,ndp=2),phr(y0,ndp=2),phr(w0),int(z0)

    lgnd = plt.legend(loc='upper right')
    lgnd.legendHandles[0]._sizes = [30]
    lgnd.legendHandles[1]._sizes = [30]
    
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
