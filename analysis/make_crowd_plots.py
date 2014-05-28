from __future__ import division
from skimage import io
from subprocess import call
#from colors import blues_r
import numpy as np
from matplotlib import pyplot as plt
import swap

#given stage1 and stage2 bureau pickles, this script produces the 4 plots currently planned for the crowd section of the SW system paper.

#user set paths
cornerplotter_path = '/Users/mbaumer/SWAP/pappy/CornerPlotter.py'
bureau_path = '/Users/mbaumer/Desktop/CFHTLS_bureau_stage1.pickle'
bureau_path2 = '/Users/mbaumer/Desktop/CFHTLS_bureau_stage2.pickle'
output_directory = '/Users/mbaumer/Desktop/'

bureau = swap.read_pickle(bureau_path, 'bureau')
bureau2 = swap.read_pickle(bureau_path2, 'bureau')
print len(bureau.list()), len(bureau2.list())

# make lists buy going through agents
N_early = 10

stage2_veteran_members = []
list1 = bureau.list()
for ID in bureau2.list():
    if ID in list1:
        stage2_veteran_members.append(ID)
print len(stage2_veteran_members), " users stayed on for Stage 2 from Stage 1"

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

for ID in bureau.list():
    agent = bureau.member[ID]
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


#same setup for stage 2, except special class is veteran users rather than "experienced" users

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

#make plots

#cumulative distribution of contribution
plt.figure(figsize=(10,8))

worth_plot1 = np.cumsum(np.sort(contribution_all)[::-1])
N1 = np.arange(worth_plot1.size) / worth_plot1.size
plt.plot(N1, worth_plot1 / worth_plot1[-1], '-b', linewidth=4, label='Stage 1: All Users')

worth_plot = np.cumsum(np.sort(contribution)[::-1])
N2 = np.arange(worth_plot.size) / worth_plot.size
plt.plot(N2, worth_plot / worth_plot[-1], '--b', linewidth=4, label='Stage 1: Experienced Users')

worth_plot = np.cumsum(np.sort(contribution_all2)[::-1])
N3 = np.arange(worth_plot.size) / worth_plot.size
plt.plot(N3, worth_plot / worth_plot[-1], '#FF8000', linewidth=4, label='Stage 2: All Users')

plt.xlabel('Fraction of Users')
plt.ylabel('Fraction of Contribution')
plt.xlim(0, 0.2)
plt.legend(loc='lower right')
plt.savefig(output_directory + 'crowd_contrib_cumul.png', bbox_inches='tight')

#final skill predicted by early skill?

plt.figure(figsize=(10,8))
plt.xlim(-0.05,0.25)
plt.ylim(-0.1,0.8)
plt.xlabel('Early Skill')
plt.ylabel('Final Skill')
plt.scatter(early_skill,final_skill,c='b',alpha=0.05)
plt.savefig(output_directory + 'early_final_skill.png', bbox_inches='tight')

# make corner plot for 5 variables of interest; stage1 = blue shaded, stage2 = orange outlines.
X = np.vstack((final_skill_all, effort_all, contribution_all, information_all, experience_all)).T

pos_filter = True
for Xi in X.T:
    pos_filter *= Xi > 0
pos_filter *= final_skill_all > 1e-7
pos_filter *= contribution_all > 1e-11
X = np.log10(X[pos_filter])

comment = 'Final Skill, Effort, Contribution, Information, Experience\n{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}'.format(
                                                                                                                                X[:, 0].min(), X[:, 0].max(),
                                                                                                                                X[:, 1].min(), X[:, 1].max(),
                                                                                                                                X[:, 2].min(), X[:, 2].max(),
                                                                                                                                X[:, 3].min(), X[:, 3].max(),
                                                                                                                                X[:, 4].min(), X[:, 4].max(),)


np.savetxt(output_directory + 'user_analysis.cpt', X, header=comment)

X = np.vstack((final_skill_all2, effort_all2, contribution_all2, information_all2, experience_all2)).T

pos_filter = True
for Xi in X.T:
    pos_filter *= Xi > 0
pos_filter *= final_skill_all2 > 1e-7
pos_filter *= contribution_all2 > 1e-11
X = np.log10(X[pos_filter])

np.savetxt(output_directory + 'user_analysis2.cpt', X, header=comment)

call([cornerplotter_path,
      '-o',
      output_directory + 'all_skill_contribution_experience_education.png',
      output_directory + 'user_analysis.cpt,blue,shaded',
      output_directory + 'user_analysis2.cpt,orange,outlines'])

#stage 2 -- new users vs. veterans: contribution.
plt.figure(figsize=(10,8))
plt.xlabel('Stage 2 Contribution')
plt.ylabel('Stage 2 Skill')
plt.scatter(contribution2, final_skill2,c='b',label='Veteran users from Stage 1')
plt.scatter(new_s2_contribution, new_s2_skill,c='#FFA500', label='New Stage 2 users')
plt.legend(loc='lower right')
plt.savefig(output_directory + 'stage2_veteran_contribution.png', bbox_inches='tight')


