#!/usr/bin/env python
# ======================================================================

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
from scipy import ndimage
#from scipy.spatial.distance import pdist
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
from sklearn.externals import joblib
from matplotlib.mlab import rec2csv

# ======================================================================

memory = joblib.Memory(cachedir='.')

def outlier_clusters(x, y, skill=None):
    data = np.vstack((x, y)).T

    dist_within = 100
    dist_max = 30
    n_clusters = 0

    clusterer = AgglomerativeClustering(n_clusters=n_clusters,
            memory=memory, compute_full_tree=True)

    # while dist_within > dist_max, keep adding clusters
    while dist_within > dist_max:
        # iterate n_clusters
        n_clusters += 1
        clusterer.set_params(n_clusters=n_clusters)

        # cluster
        labels = clusterer.fit_predict(data)

        # get cluster_centers
        cluster_labels = range(n_clusters)
        cluster_centers = np.array([np.mean(data[labels == i], axis=1)
                                    for i in cluster_labels])

        # find dist_within: the maximum pairwise distance inside a cluster
        dist_within = np.max([pairwise_distances(data[labels == i]
                              for i in cluster_labels], axis=1)


    # clear memory
    memory.clear()

    return cluster_centers, cluster_labels, labels, n_clusters

## def outlier_clusters_old(x, y, skill=None, linkage_type='single'):
##     # TODO: incorporate skill
##     data = np.vstack((x, y)).T
##     cluster_labels = np.arange(len(data))
##     cluster_centers = data.copy()
##     cluster_center_labels = np.arange(len(data))
##     dist_min = 0  # escape clause
##     dist_max = 30  # maximum distance we care about for agglomerative clustering
##     # now agglomeratively cluster the clusters
##     while dist_min < dist_max:
##         dist_list = []
##         for cluster_i in range(len(cluster_centers)):
##             for cluster_j in range(cluster_i + 1, len(cluster_centers)):
## 
##                 cluster_label_i = cluster_center_labels[cluster_i]
##                 members_i = (cluster_labels == cluster_label_i)
##                 data_i = data[members_i]
##                 cluster_label_j = cluster_center_labels[cluster_j]
##                 members_j = (cluster_labels == cluster_label_j)
##                 data_j = data[members_j]
##                 dists = np.array(
##                         [[pdist([data_im, data_jn]) for data_im in data_i]
##                         for data_jn in data_j])
## 
##                 if linkage_type == 'complete':
##                     # do cluster distance from the biggest difference;
##                     # complete linkage clustering
##                     dist = np.max(dists)
##                 elif linkage_type == 'single':
##                     # do cluster distance from the smallest difference;
##                     # single linkage clustering
##                     dist = np.min(dists)
## 
##                 if dist < dist_max:
##                     dist_list.append([cluster_i, cluster_j, dist])
##         dist_list = np.array(dist_list)
## 
##         # the min length requirement is because we could have
##         # no clusters < dist_max
##         if len(dist_list) > 0:
##             # now take the smallest distance pair and merge them
##             cluster_i, cluster_j, dist_min = dist_list[
##                     np.argmin(dist_list[:, -1])]
##             cluster_i = np.int(cluster_i)
##             cluster_j = np.int(cluster_j)
##             cluster_centers_indx = np.arange(len(cluster_centers))
## 
##             new_clusters = cluster_centers[
##                     (cluster_centers_indx != cluster_i) *
##                     (cluster_centers_indx != cluster_j)]
##             new_cluster_center_labels = cluster_center_labels[
##                     (cluster_centers_indx != cluster_i) *
##                     (cluster_centers_indx != cluster_j)]
## 
##             merged_cluster = np.mean(
##                     [cluster_centers[cluster_i], cluster_centers[cluster_j]],
##                     axis=0)
##             merged_cluster_label = cluster_center_labels[
##                     (cluster_centers_indx == cluster_i)]
## 
##             cluster_labels = np.where(
##                     cluster_labels == cluster_center_labels[
##                         (cluster_centers_indx == cluster_j)],
##                     cluster_center_labels[(cluster_centers_indx == cluster_i)],
##                     cluster_labels)
## 
##             cluster_centers = np.vstack((new_clusters, merged_cluster))
##             cluster_center_labels = np.hstack(
##                     (new_cluster_center_labels, merged_cluster_label))
## 
##         else:
##             # escape clause
##             dist_min = dist_max
## 
##     n_clusters = len(cluster_centers)
##     return cluster_centers, cluster_center_labels, cluster_labels, n_clusters


# ======================================================================

def make_lens_catalog(argv):
    """
    NAME
        make_lens_catalog

    PURPOSE
        Given location of collection pickle, this script produces a set of
        annotated images of lenses (heatmaps for lens locations, markers for
        where clicks were, etc).

    COMMENTS
        You have to download the file so it chooses whever your output
        directory is to also download the raw images.
        This should be pretty customizable.

    FLAGS
        -h              Print this message

        --skill         Weight by skill


    INPUTS
        collection.pickle

    OUTPUTS
        lens.dat
            Assumed format:
            ID   kind   x   y    P     N0   S

            Here:
            ID = Space Warps subject ID
            kind = Space Warps subject type (sim, dud, test) 
            x,y = object (cluster) centroid, in pixels
            P = Space Warps subject probability
            N0 = number of markers in the cluster
            S = total skill per cluster, summed over markers

    EXAMPLE

    BUGS

    AUTHORS
        This file is part of the Space Warps project, and is distributed
        under the GPL v2 by the Space Warps Science Team.
        http://spacewarps.org/

    HISTORY
        2013-07-16  started Davis (KIPAC)
    """

    try:
        opts, args = getopt.getopt(argv,"h",
                ["help", "heatmap", "contour", "field", "stamp", "alpha",
                 "points", "skill"])
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        print make_lens_catalog.__doc__  # will print the big comment above.
        return

    flags = {'skill': False}

    for o,a in opts:
        if o in ("-h", "--help"):
            print make_lens_catalog.__doc__
            return
        elif o in ("--skill"):
            flags['skill'] = True
        else:
            assert False, "unhandled option"

    # Check for pickles in array args:
    if len(args) == 1:
        collection_path = args[0]
        print "make_lens_catalog: illustrating behaviour captured in collection file: "
        print "make_lens_catalog: ",collection_path

    else:
        print make_lens_catalog.__doc__
        return

    output_directory = './'

    dtype_catalog = np.dtype({'names':
        ('id', 'kind', 'x', 'y', 'p', 'n0', 's'),
        'formats': ('|S24', '|S15', np.float, np.float,
                    np.float, np.int, np.float)})

    catalog_path = output_directory + 'catalog.dat'
    F = open(catalog_path, 'w')
    F.write('id,kind,x,y,p,n0,s\n')

    # ------------------------------------------------------------------
    # Read in files:

    collection = swap.read_pickle(collection_path, 'collection')

    print "make_lens_catalog: collection numbers ", len(collection.list())

    # ------------------------------------------------------------------
    # Run through data:

    catalog = []
    for ID in collection.list():

        subject = collection.member[ID]
        kind = subject.kind
        P = subject.mean_probability


        itwas = subject.annotationhistory['ItWas']
        x_all = subject.annotationhistory['At_X']
        y_all = subject.annotationhistory['At_Y']

        x_markers = np.array([xi for xj in x_all for xi in xj])
        y_markers = np.array([yi for yj in y_all for yi in yj])

        PL_all = subject.annotationhistory['PL']
        PD_all = subject.annotationhistory['PD']

        # filter out the empty clicks
        PL_list = []
        for i, xj in enumerate(x_all):
            PL_list.append([PL_all[i]] * len(xj))
        PL = np.array([PLi for PLj in PL_list for PLi in PLj])

        # filter out the empty clicks
        PD_list = []
        for i, xj in enumerate(x_all):
            PD_list.append([PD_all[i]] * len(xj))
        PD = np.array([PDi for PDj in PD_list for PDi in PDj])

        skill = swap.expectedInformationGain(0.5, PL, PD)  # skill


        # ------------------------------------------------------------------
        # cluster
        if flags['skill']:
            cluster_centers, cluster_center_labels, cluster_labels, \
                    n_clusters = outlier_clusters(x_markers, y_markers, skill)
        else:
            cluster_centers, cluster_center_labels, cluster_labels, \
                    n_clusters = outlier_clusters(x_markers, y_markers, None)
        # need to get: x, y, N0, S

        # bit of a hack since I don't want to sit through and work this out on
        # my internet-less laptop...
        multiple_clicks = [list(cluster_center_labels).index(ij)
                           for ij in cluster_center_labels
                           if list(cluster_labels).count(ij) > 1]
        for cluster_ij in multiple_clicks:#range(n_clusters):
            cluster_center = cluster_centers[cluster_ij]
            cluster_label = cluster_center_labels[cluster_ij]
            members = (cluster_labels == cluster_label)

            x, y = cluster_center
            N0 = np.sum(members)
            S = np.sum(skill[members])

            catalog.append((ID, kind, x, y, P, N0, S))
            if len(catalog)%500 == 0:
                print len(catalog)
            F.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(
                ID, kind, x, y, P, N0, S))
    F.close()

    # convert into array
    catalog = np.array(catalog, dtype=dtype_catalog)
    # save catalog!
    rec2csv(catalog, catalog_path)

# ======================================================================

if __name__ == '__main__':
    make_lens_catalog(sys.argv[1:])

# ======================================================================
