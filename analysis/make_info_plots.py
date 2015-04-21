#!/usr/bin/env python

from subprocess import call

import sys,getopt,numpy as np

import matplotlib
from pylab import *;

import swap

def make_info_plots(argv):
    """
    NAME
        make_info_plots

    PURPOSE
        Given stage1 and stage2 bureau pickles, this script produces the 
        several plots for the crowd analysis

    COMMENTS

    FLAGS
        -h                Print this message

    INPUTS
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
      2014-06-27  started More & More (Kavli IPMU)

    """
    # ------------------------------------------------------------------

    try:
       opts, args = getopt.getopt(argv,"h",["help"])
    except getopt.GetoptError, err:
       print str(err) # will print something like "option -a not recognized"
       print make_info_plots.__doc__  # will print the big comment above.
       return


    for o,a in opts:
       if o in ("-h", "--help"):
          print make_info_plots.__doc__
          return
       else:
          assert False, "unhandled option"

    # Check for pickles in array args:
    if len(args) == 2:
        bureau1_path = args[0]
        bureau2_path = args[1]
        print "make_info_plots: illustrating behaviour captured in bureau files: "
        print "make_info_plots: ",bureau1_path
        print "make_info_plots: ",bureau2_path
    else:
        print make_info_plots.__doc__
        return


    # Read in bureau objects:

    bureau1 = swap.read_pickle(bureau1_path, 'bureau')
    bureau2 = swap.read_pickle(bureau2_path, 'bureau')
    print "make_info_plots: stage 1, 2 agent numbers: ",len(bureau1.list()), len(bureau2.list())
    
    experience1 = []
    effort1 = []
    final_skill1 = []
    final_PL1 =[]
    final_PD1 =[]
    information1 = []
    contribution1 = []
    
    experience2 = []
    effort2 = []
    final_skill2 = []
    final_PL2 =[]
    final_PD2 =[]
    information2 = []
    contribution2 = []
##  
    Ntrajectory=50
    for ID in bureau1.list():
        agent = bureau1.member[ID]

        effort1.append(agent.N-agent.NT)
        experience1.append(agent.NT)
        final_skill1.append(agent.traininghistory['Skill'][-1])
        final_PL1.append(np.mean(agent.get_PL_realization(Ntrajectory)))
        final_PD1.append(np.mean(agent.get_PD_realization(Ntrajectory)))
        information1.append(agent.testhistory['I'].sum())
        contribution1.append(agent.testhistory['Skill'].sum()) 
        
    
    for ID in bureau2.list():
        agent = bureau2.member[ID]

        effort2.append(agent.N-agent.NT)
        experience2.append(agent.NT)
        final_skill2.append(agent.traininghistory['Skill'][-1])
        final_PL2.append(np.mean(agent.get_PL_realization(Ntrajectory)))
        final_PD2.append(np.mean(agent.get_PD_realization(Ntrajectory)))
        information2.append(agent.testhistory['I'].sum())
        contribution2.append(agent.testhistory['Skill'].sum()) 
    
## PL-PD plot
    def plotplpd(xx,yy,zz,which,ztitle):
        bins=100;
        ax=subplot(2,2,which,aspect=1.);
        hist2d(xx,yy,bins,weights=zz,norm=matplotlib.colors.LogNorm());
        cbar=colorbar();
        cbar.solids.set_edgecolor("face");
        ax.set_xlabel("P$_L$");
        ax.set_ylabel("P$_D$");
        ax.set_title(ztitle);
        ax.set_xlim(0,1);
        ax.set_ylim(0,1);
        xx=np.arange(-0.1,2,0.1); 
        ax.axhline(0.5,color="k",linestyle='dashed');
        ax.axvline(0.5,color="k",linestyle='dashed');
        ax.plot(xx,1-xx,color="k");
 

    ###########################
    ##Users
    ###########################
    plotplpd(final_PL1,final_PD1,None,1,"Stage1 Users")
    plotplpd(final_PL2,final_PD2,None,2,"Stage2 Users")
    savefig("users_plpd.png")
    clf();    
    ###########################
    ##Effort
    ###########################
    plotplpd(final_PL1,final_PD1,effort1,1,"Stage 1 Effort")
    plotplpd(final_PL2,final_PD2,effort2,2,"Stage 2 Effort")
    savefig("effort_plpd.png")
    clf();    

    ###########################
    ##Experience
    ###########################
    plotplpd(final_PL1,final_PD1,experience1,1,"Stage 1 Experience")
    plotplpd(final_PL2,final_PD2,experience2,2,"Stage 2 Experience");
    savefig("experience_plpd.png")
    clf();    

    ###########################
    ##Contribution 
    ###########################
    plotplpd(final_PL1,final_PD1,contribution1,1,"Stage 1 Contribution")
    plotplpd(final_PL2,final_PD2,contribution2,2,"Stage 2 Contribution")
    savefig("contribution_plpd.png")
    clf();    

    ###########################
    ##Average Information 
    ###########################
    plotplpd(final_PL1,final_PD1,information1,1,"Stage 1 Information")
    plotplpd(final_PL2,final_PD2,information2,2,"Stage 2 Information")
    savefig("information_plpd.png")
    clf();    

    ###########################
    ##Skill PL PD plot
    ###########################
    bins=101
    skill=np.zeros(bins*bins);
    skill=np.reshape(skill,(bins,bins));
    for ii in range(bins):
        M_ll=0.01*ii;
        for jj in range(bins):
            M_nn=0.01*jj;
            skill[ii][jj]=swap.expectedInformationGain(0.5, M_ll, M_nn);
 
    ax=subplot(1,1,1);
    im=ax.imshow(skill,origin='lower',extent=(0,1,0,1));
    cbar=colorbar(im);
    cbar.solids.set_edgecolor("face");

    ax.set_xlim(0,1);
    ax.set_ylim(0,1);
    ax.set_xlabel("P$_L$");
    ax.set_ylabel("P$_D$");
    ax.set_title("Skill");
    xx=np.arange(-0.1,2,0.1); 
    ax.axhline(0.5,color="k",linestyle='dashed');
    ax.axvline(0.5,color="k",linestyle='dashed');
    ax.plot(xx,1-xx,color="k");
   
    savefig("skill_plpd.png")    
    clf();    

    ###########################
    ## Cumulative effort and users vs. skill 
    ###########################
    bins=100
    ax=subplot(2,2,1);
    hist(final_skill1,bins,cumulative=True,normed=1,color=(0.8,0.2,0.2),histtype='stepfilled',label="Users",range=(0,1));
    hist(final_skill1,bins,weights=effort1, cumulative=True,color=(1.0,0.7,0.5),normed=1,histtype='stepfilled',label="Effort",range=(0,1));
    ax.set_xlabel("Skill");
    ax.set_ylim(0,1.)
    ax.set_ylabel("Cumulative Fraction");
    ax.set_title("Stage 1")
    legend(loc=4);

    ax=subplot(2,2,2);
    hist(final_skill2,bins,cumulative=True,normed=1,color=(0.8,0.2,0.2),histtype='stepfilled',label="Users",range=(0,1));
    hist(final_skill2,bins,weights=effort2, cumulative=True,color=(1.0,0.7,0.5),normed=1,histtype='stepfilled',label="Effort",range=(0,1));
    ax.set_xlabel("Skill");
    ax.set_ylim(0,1.)
    ax.set_ylabel("Cumulative Fraction");
    ax.set_title("Stage 2")
    legend(loc=4);
    savefig("skill_effort_users_cum.png")
    clf();    


    ###########################
    ## Training histories of first 20 agents with final skill > 0.5 and <0.5 for Stage 1 and 2 
    ###########################

    final_skill1=np.array(final_skill1)
    idx=(final_skill1>0.5)
    idxl=(final_skill1<0.5)
    ax=subplot(2,2,1);
    ax.set_xscale('log');
    ax.set_xlabel("Experience")
    ax.set_ylabel("Skill")
    ax.set_title("Stage1")
    ii=0;
    for idxx,ID in zip(idx,bureau1.list()):
        if(ii>20):
            break;
        if(not idxx):
            continue;
        agent = bureau1.member[ID]
         
        I = agent.traininghistory['Skill']
        N = np.linspace(1, len(I), len(I), endpoint=True)
        
        # Information contributions:
        ax.plot(N, I, color="green", alpha=0.2, linewidth=2.0, linestyle="-")
        ax.scatter(N[-1], I[-1], color="green", alpha=0.5)
        ii=ii+1
    
    ii=0;
    for idxx,ID in zip(idxl,bureau1.list()):
        if(ii>20):
            break;
        if(not idxx):
            continue;
        agent = bureau1.member[ID]
         
        I = agent.traininghistory['Skill']
        N = np.linspace(1, len(I), len(I), endpoint=True)
        
        # Information contributions:
        ax.plot(N, I, color="red", alpha=0.2, linewidth=2.0, linestyle="-")
        ax.scatter(N[-1], I[-1], color="red", alpha=0.5)
        ii=ii+1

    final_skill2=np.array(final_skill2)
    idx=(final_skill2>0.5)
    idxl=(final_skill2<0.5)
    ax=subplot(2,2,2);
    ax.set_xscale('log');
    ax.set_xlabel("Experience")
    ax.set_ylabel("Skill")
    ax.set_title("Stage2")
 
    for idxx,ID in zip(idx,bureau2.list()):
        if(not idxx):
            continue;
        agent = bureau2.member[ID]
         
        I = agent.traininghistory['Skill']
        N = np.linspace(1, len(I), len(I), endpoint=True)
        
        # Information contributions:
        ax.plot(N, I, color="green", alpha=0.2, linewidth=2.0, linestyle="-")
        ax.scatter(N[-1], I[-1], color="green", alpha=0.5)
    
    ii=0;
    for idxx,ID in zip(idxl,bureau2.list()):
        if(ii>20):
            break;
        if(not idxx):
            continue;
        agent = bureau2.member[ID]
         
        I = agent.traininghistory['Skill']
        N = np.linspace(1, len(I), len(I), endpoint=True)
        
        # Information contributions:
        ax.plot(N, I, color="red", alpha=0.2, linewidth=2.0, linestyle="-")
        ax.scatter(N[-1], I[-1], color="red", alpha=0.5)
        ii=ii+1

    tight_layout();
    savefig("skill_experience.png")    

    clf();
    ###########################
    ## function to plot 2d histograms
    ###########################

    def plothist2d(xx,yy,zz,which,xlab,ylab,ztitle):
        bins=100;
        ax=subplot(2,2,which);
        xx=np.array(xx)
        yy=np.array(yy)
        zz=np.array(zz)
        idx=np.where(xx>0)
        hist2d(np.log10(xx[idx]),yy[idx],bins,weights=zz[idx],norm=matplotlib.colors.LogNorm());
        cbar=colorbar();
        cbar.solids.set_edgecolor("face");
 
        ax.set_xlabel(xlab);
        ax.set_ylabel(ylab);
        ax.set_title(ztitle);

    ###########################
    ## Contribution as a function of experience vs. skill 
    ###########################
    plothist2d(experience1,final_skill1,contribution1,1,"Log(Experience)","Skill","Stage 1 Contribution")
    plothist2d(experience2,final_skill2,contribution2,2,"Log(Experience)","Skill","Stage 2 Contribution")
    savefig("experience_skill_contribution.png")
    clf();  

    ###########################
    ## Contribution as a function of effort vs. skill 
    ###########################
    plothist2d(effort1,final_skill1,contribution1,1,"Log(Effort)","Skill","Stage 1 Contribution")
    plothist2d(effort2,final_skill2,contribution2,2,"Log(Effort)","Skill","Stage 2 Contribution")
    savefig("effort_skill_contribution.png")
    clf();  


if __name__ == '__main__': 
    make_info_plots(sys.argv[1:])

