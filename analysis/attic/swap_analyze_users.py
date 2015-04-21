
# coding: utf-8

# # Analyze CFHTLS Pickle

# In[210]:

from skimage import io
from subprocess import call
#from colors import blues_r
import numpy as np
from matplotlib import pyplot as plt
import swap

#cornerplotter_path = '/Users/cpd/SWAP/pappy/CornerPlotter.py'
#bureau_path = '/Users/cpd/SWAP/SpaceWarps/analysis/CFHTLS_bureau.pickle'
#output_directory = '/Users/cpd/SWAP/swap_analysis/'

cornerplotter_path = '/Users/mbaumer/SWAP/pappy/CornerPlotter.py'
bureau_path = '/Users/mbaumer/SpaceWarps/analysis/CFHTLS_bureau.pickle'
output_directory = '/Users/mbaumer/SWAP/swap_analysis'

bureau = swap.read_pickle(bureau_path, 'bureau')
len(bureau.list())

# make lists buy going through agents
N_early = 10

skill = []
contribution = []
experience = []
education = []
early_contribution = []
early_skill = []
skill_all = []
contribution_all = []
experience_all = []
education_all = []
for ID in bureau.list():
    agent = bureau.member[ID]
    skill_all.append(agent.traininghistory['Skill'][-1])
    contribution_all.append(agent.testhistory['I'].sum())
    experience_all.append(agent.N)
    education_all.append(agent.NT)
    if agent.NT < N_early:
        continue

    skill.append(agent.traininghistory['Skill'][-1])
    contribution.append(agent.testhistory['I'].sum())
    experience.append(agent.N)
    education.append(agent.NT)
    early_contribution.append(agent.testhistory['I'][:N_early].sum())
    early_skill.append(agent.traininghistory['Skill'][N_early])

experience = np.array(experience)
education = np.array(education)
skill = np.array(skill)
contribution = np.array(contribution)
experience_all = np.array(experience_all)
education_all = np.array(education_all)
skill_all = np.array(skill_all)
contribution_all = np.array(contribution_all)
early_contribution = np.array(early_contribution)
early_skill = np.array(early_skill)

# make plots

plt.figure(figsize=(10,8))
worth_plot = np.cumsum(np.sort(contribution)[::-1])
N = np.arange(worth_plot.size) / worth_plot.size
plt.plot(N, worth_plot / worth_plot[-1], '-b', linewidth=4, label='Educated Users')


worth_plot = np.cumsum(np.sort(contribution_all)[::-1])
N = np.arange(worth_plot.size) / worth_plot.size
plt.plot(N, worth_plot / worth_plot[-1], '--b', linewidth=4, label='All Users')
plt.xlabel('Fraction of Users')
plt.ylabel('Fraction of Contribution')
plt.xlim(0, 0.1)
plt.legend(loc='lower right')

plt.figure(figsize=(10,8))
worth_plot = np.cumsum(np.sort(skill)[::-1])
N = np.arange(worth_plot.size) / worth_plot.size
plt.plot(N, worth_plot / worth_plot[-1], '-b', linewidth=4, label='Educated Users')

worth_plot = np.cumsum(np.sort(skill_all)[::-1])
N = np.arange(worth_plot.size) / worth_plot.size
plt.plot(N, worth_plot / worth_plot[-1], '--b', linewidth=4, label='All Users')
plt.xlabel('Fraction of Users')
plt.ylabel('Fraction of Total Skill')
plt.legend(loc='lower right')


# In[211]:

vallist = [{'array': early_skill,
            'name': 'Skill at $N_T$ = {0}'.format(N_early),
            'min': 1e-3},
           {'array': early_contribution,
            'name': 'Total Contribution at $N_T$ = {0}'.format(N_early),
            'min': 1e-11},
           {'array': contribution,
            'name': 'Total Contribution',
            'min': 1e-11},
           {'array': skill,
            'name': 'Final Skill',
            'min': 1e-3},
           {'array': education,
            'name': 'Education',
            'min': 1},
           {'array': experience,
            'name': 'Experience',
            'min': 1},
            ]

# make corner plot for educated
X = np.vstack((skill, contribution, experience, education)).T

pos_filter = True
for Xi in X.T:
    pos_filter *= Xi > 0
pos_filter *= skill > 1e-7
pos_filter *= contribution > 1e-11
X = np.log10(X[pos_filter])

comment = 'Skill, Contribution, Experience, Education\n{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(
    X[:, 0].min(), X[:, 0].max(),
    X[:, 1].min(), X[:, 1].max(),
    X[:, 2].min(), X[:, 2].max(),
    X[:, 3].min(), X[:, 3].max(),)

np.savetxt('user_analysis.cpt', X, header=comment)
call([cornerplotter_path,
      '-o',
      output_directory + '/skill_contribution_experience_education.png',
      output_directory + '/user_analysis.cpt,blue,shaded'])


# make corner plot for all
X = np.vstack((skill_all, contribution_all, experience_all, education_all)).T

pos_filter = True
for Xi in X.T:
    pos_filter *= Xi > 0
pos_filter *= skill_all > 1e-7
pos_filter *= contribution_all > 1e-11
X = np.log10(X[pos_filter])

comment = 'Skill, Contribution, Experience, Education\n{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(
    X[:, 0].min(), X[:, 0].max(),
    X[:, 1].min(), X[:, 1].max(),
    X[:, 2].min(), X[:, 2].max(),
    X[:, 3].min(), X[:, 3].max(),)

np.savetxt('user_analysis.cpt', X, header=comment)
call([cornerplotter_path,
      '-o',
      output_directory + '/all_skill_contribution_experience_education.png',
      output_directory + '/user_analysis.cpt,blue,shaded'])



# make corner plot looking at early contributions
X = np.vstack((early_skill, early_contribution, skill, contribution)).T

pos_filter = True
for Xi in X.T:
    pos_filter *= Xi > 0
pos_filter *= skill > 1e-7
pos_filter *= contribution > 1e-11
pos_filter *= early_skill > 1e-7
pos_filter *= early_contribution > 1e-11
X = np.log10(X[pos_filter])

comment = 'Early Skill, Early Contribution, Skill, Contribution,\n{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(
    X[:, 0].min(), X[:, 0].max(),
    X[:, 1].min(), X[:, 1].max(),
    X[:, 2].min(), X[:, 2].max(),
    X[:, 3].min(), X[:, 3].max(),)

np.savetxt('user_analysis.cpt', X, header=comment)
call([cornerplotter_path,
      '-o',
      output_directory + '/early_skill_contribution.png',
      output_directory + '/user_analysis.cpt,blue,shaded',])


# In[212]:

io.Image(plt.imread(output_directory + '/skill_contribution_experience_education.png'))


# In[213]:

io.Image(plt.imread(output_directory + '/all_skill_contribution_experience_education.png'))


# In[214]:

io.Image(plt.imread(output_directory + '/early_skill_contribution.png'))


# In[70]:



