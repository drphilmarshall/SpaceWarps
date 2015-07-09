import numpy as np
import pandas as pd
import swap

def logit(x):
    return np.log(x / (1 - x))
def inv_logit(x):
    return 1. / (1 + np.exp(-x))

###############################################################################
# load up data
###############################################################################
base_collection_path = '/nfs/slac/g/ki/ki18/cpd/swap/pickles/15.07.04/'
knownlenspath = base_collection_path + 'knownlens.csv'
knownlens = pd.read_csv(knownlenspath, index_col=0)

stages = [2, 1]
lines = ['offline', 'offline_supervised_and_unsupervised', 'online']

collections = {}
for stage in stages:
    for line in lines:
        annotated_catalog_path = base_collection_path + 'stage{0}_{1}'.format(stage, line) + '/annotated_collection.csv'
        collection = pd.read_csv(annotated_catalog_path, index_col=0,
                                 usecols=['ID', 'ZooID', 'mean_probability', 'kind'])
        # augment with knownlens
        collection['knownlens'] = collection['ZooID'].apply(lambda x: x in knownlens['ZooID'].values)
        collection['logit_prob'] = collection['mean_probability'].apply(logit)
        collections[(stage, line)] = collection

# update the offline to have the online parameters
for stage in stages:
    col = collections[(stage, 'online')]
    collections[(stage, 'offline')]['logit_prob_online'] = col['logit_prob']
    collections[(stage, 'offline')]['mean_probability_online'] = col['mean_probability']

    col = collections[(stage, 'offline_supervised_and_unsupervised')]
    collections[(stage, 'offline')]['logit_prob_alldata'] = col['logit_prob']
    collections[(stage, 'offline')]['mean_probability_alldata'] = col['mean_probability']


###############################################################################
# Select Datasets
###############################################################################
from os import makedirs
out_directory = '/u/ki/cpd/public_html/targets'
makedirs(out_directory)

stage = 1
# all stage1 sims and duds
col = collections[(stage, 'offline')]
train = col[(col['kind'] == 'sim') | (col['kind'] == 'dud')]
train.to_csv(out_directory + '/train_{0}.csv'.format(stage))
print('train', len(train))  # 10210

# all stage1 knownlens
known = col[col['knownlens']]
known.to_csv(out_directory + '/known_{0}.csv'.format(stage))
print('known', len(known))  # 212

# stage1 high offline low online
# note that the ROC curve takes relatively low p for classification
high_chance = col[(col['mean_probability'] > 0.35) &
                  (col['mean_probability_online'] < 0.01) &
                  (col['kind'] == 'test')]
high_chance.to_csv(out_directory + '/high_chance_{0}.csv'.format(stage))
print('high_chance', len(high_chance))  # 1594


# stage1 high offline low online for unsupervised_and_supervised
high_chance_all = col[(col['mean_probability_alldata'] > 0.7) &
                      (col['mean_probability_online'] < 0.01) &
                      (col['kind'] == 'test')]
high_chance_all.to_csv(out_directory + '/high_chance_unsup_{0}.csv'.format(stage))
print('high_chance_all', len(high_chance_all))  # 1808. 2057 unique

import ipdb; ipdb.set_trace()

# stage1 low offline high online
low_chance = col[(col['mean_probability'] < 0.5) &
                 (col['mean_probability_online'] > 0.9) &
                 (col['kind'] == 'test')]
low_chance.to_csv(out_directory + '/low_chance_{0}.csv'.format(stage))
print('low_chance', len(low_chance))


# stage1 low offline high online for unsupervised_and_supervised
low_chance_all = col[(col['mean_probability_alldata'] < 0.8) &
                     (col['mean_probability_online'] > 0.9) &
                     (col['kind'] == 'test')]
low_chance_all.to_csv(out_directory + '/low_chance_unsup_{0}.csv'.format(stage))
print('low_chance_all', len(low_chance_all))



