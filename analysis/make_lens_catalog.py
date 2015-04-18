#!/usr/bin/env python
# ======================================================================

import numpy as np

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
from matplotlib.mlab import csv2rec
from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.metrics import pairwise_distances
from sklearn.externals import joblib

# ======================================================================


def outlier_clusters_dbscan(x, y, skill=None, memory=None,
                            eps=25, min_samples=5):
    # TODO: incorporate skill
    data = np.vstack((x, y)).T

    if len(data) == 0:
        # uh.
        print 'clustering: NO cluster members!'
        cluster_centers = np.array([[-1, -1]])
        cluster_labels = []
        labels = []
        n_clusters = 0
        dist_within = np.array([])

    elif len(data) == 1:
        print 'clustering: only 1 data point!'
        cluster_centers = data
        cluster_labels = [0]
        labels = np.array([0])
        n_clusters = 1
        dist_within = np.array([0])

    else:

        clusterer = DBSCAN(eps=eps, min_samples=min_samples)
        db = clusterer.fit(data)
        labels = db.labels_
        n_clusters = len(set(labels))
        cluster_labels = list(set(labels))
        cluster_centers = np.array([np.mean(data[labels == i], axis=0)
                                    for i in cluster_labels])

    # print n_clusters
    # print labels

    dist_within_final = np.array([np.max(pairwise_distances(
            data[labels == i])) for i in cluster_labels])

    return cluster_centers, cluster_labels, labels, n_clusters, dist_within_final

def outlier_clusters_ward(x, y, skill=None, memory=None):
    # TODO: incorporate skill
    data = np.vstack((x, y)).T

    if len(data) == 0:
        # uh.
        print 'clustering: NO cluster members!'
        cluster_centers = np.array([[-1, -1]])
        cluster_labels = []
        labels = []
        n_clusters = 0
        dist_within = np.array([])

    elif len(data) == 1:
        print 'clustering: only 1 data point!'
        cluster_centers = data
        cluster_labels = [0]
        labels = np.array([0])
        n_clusters = 1
        dist_within = np.array([0])

    else:
        dist_within = 1000
        dist_max = 75
        n_clusters = 0
        n_clusters_max = 10

        clusterer = AgglomerativeClustering(n_clusters=n_clusters,
                memory=memory)

        # while dist_within > dist_max, keep adding clusters
        while (dist_within > dist_max) * (n_clusters < n_clusters_max):
            # iterate n_clusters
            n_clusters += 1
            clusterer.set_params(n_clusters=n_clusters)

            # cluster
            labels = clusterer.fit_predict(data)

            # get cluster_centers
            cluster_labels = range(n_clusters)
            cluster_centers = np.array([np.mean(data[labels == i], axis=0)
                                        for i in cluster_labels])

            # find dist_within: the maximum pairwise distance inside a cluster
            dist_within = np.max([np.max(pairwise_distances(
                                  data[labels == i]))
                                  for i in cluster_labels])

    dist_within_final = np.array([np.max(pairwise_distances(
            data[labels == i])) for i in cluster_labels])

    return cluster_centers, cluster_labels, labels, n_clusters, dist_within_final


outlier_clusters = outlier_clusters_dbscan

# ======================================================================

def make_lens_catalog(args):
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
            ID   kind   x   y    Prob     N0   Skill   Dist

            Here:
            ID = Space Warps subject ID
            kind = Space Warps subject type (sim, dud, test)
            x,y = object (cluster) centroid, in pixels
            P = Space Warps subject probability
            N0 = number of markers in the cluster
            S = total skill per cluster, summed over markers
            D = biggest distance within cluster

    EXAMPLE

    BUGS

    AUTHORS
        This file is part of the Space Warps project, and is distributed
        under the MIT license by the Space Warps Science Team.
        http://spacewarps.org/

    HISTORY
        2013-07-16  started Davis (KIPAC)
    """

    # ------------------------------------------------------------------
    # Some defaults:

    flags = {'skill': False,
             'output_directory': './',
             'output_name': 'catalog.dat',
             'image_y_size': 440,
             'catalog_path': '',
             'update_collection': '',}

    # ------------------------------------------------------------------
    # Read in options:

    # this has to be easier to do...
    for arg in args:
        if arg in flags:
            flags[arg] = args[arg]
        elif arg == 'collection_path':
            collection_path = args[arg]
        else:
            print "make_lens_atlas: unrecognized flag ",arg

    print "make_lens_catalog: illustrating behaviour captured in collection file: "
    print "make_lens_catalog: ",collection_path

    memory = joblib.Memory(cachedir=flags['output_directory'])
    memory.clear()

    catalog_path = flags['output_directory'] + flags['output_name']
    if len(flags['output_name']) > 0:
        F = open(catalog_path, 'w')
        F.write('id,kind,x,y,prob,n0,skill,dist\n')

    # ------------------------------------------------------------------
    # Read in files:

    collection = swap.read_pickle(collection_path, 'collection')
    ID_list = collection.list()
    print "make_lens_catalog: collection numbers ", len(ID_list)

    if flags['catalog_path'] != '':
        print "make_lens_catalog: filtering from catalog ",flags['catalog_path']
        catalog_in = csv2rec(flags['catalog_path'])
        ID_list = np.unique(catalog_in['id'])

    # ------------------------------------------------------------------
    # Run through data:

    catalog = {}
    for ID in ID_list:

        subject = collection.member[ID]
        kind = subject.kind
        P = subject.mean_probability


        itwas = subject.annotationhistory['ItWas']
        x_all = subject.annotationhistory['At_X']
        y_all = subject.annotationhistory['At_Y']

        x_markers = np.array([xi for xj in x_all for xi in xj])
        y_markers = np.array([yi for yj in y_all for yi in yj])

        catalog.update({ID: {'agents_reject': [],
                             'x': x_markers,
                             'y': y_markers,}})
        PL_all = subject.annotationhistory['PL']
        PD_all = subject.annotationhistory['PD']

        # filter out the empty clicks
        PL_list = []
        PL_nots = []
        for i, xj in enumerate(x_all):
            # len(xj) of empty = 0
            PL_list.append([PL_all[i]] * len(xj))
            if len(xj) == 0:
                PL_nots.append(PL_all[i])
        PL = np.array([PLi for PLj in PL_list for PLi in PLj])
        PL_nots = np.array(PL_nots)

        # filter out the empty clicks
        PD_list = []
        PD_nots = []
        for i, xj in enumerate(x_all):
            PD_list.append([PD_all[i]] * len(xj))
            if len(xj) == 0:
                PD_nots.append(PD_all[i])
                catalog[ID]['agents_reject'].append(i)
        PD = np.array([PDi for PDj in PD_list for PDi in PDj])
        PD_nots = np.array(PD_nots)

        skill = swap.expectedInformationGain(0.5, PL, PD)  # skill

        # it is only fair to write out the NOTs, too
        # do the empty guys
        skill_nots = swap.expectedInformationGain(0.5, PL_nots, PD_nots)  # skill

        x, y = -1, -1
        N0 = len(skill_nots)
        S = np.sum(skill_nots)
        D = 0

        ## catalog.append((ID, kind, x, y, P, N0, S, D))
        if len(catalog)%500 == 0:
            print len(catalog)
        if len(flags['output_name']) > 0:
            F.write('{0},{1},{2},{3},{4},{5},{6},{7}\n'.format(
                ID, kind, x, y, P, N0, S, D))

        if len(x_markers) == 0:
            # apparently everyone was a not...
            catalog[ID]['agents_labels'] = np.array([])
            continue

        # ------------------------------------------------------------------
        # cluster
        print 'make_lens_catalog: subject ID = ', ID
        if flags['skill']:
            cluster_centers, cluster_center_labels, cluster_labels, \
                    n_clusters, dist_within = outlier_clusters(x_markers, y_markers, skill, memory=memory)
        else:
            cluster_centers, cluster_center_labels, cluster_labels, \
                    n_clusters, dist_within = outlier_clusters(x_markers, y_markers, None, memory=memory)
        # need to get: x, y, N0, S

        catalog[ID]['agents_labels'] = cluster_labels

        for cluster_center_label in cluster_center_labels:
            cluster_center = cluster_centers[cluster_center_label]
            members = (cluster_labels == cluster_center_label)

            x, y = cluster_center
            # convert y to catalog convention
            y = flags['image_y_size'] - y
            N0 = np.sum(members)
            S = np.sum(skill[members])
            D = dist_within[cluster_center_label]

            if cluster_center_label == -1:
                # outlier cluster
                # so really every point is its own cluster...
                D = 0
            ## catalog.append((ID, kind, x, y, P, N0, S, D))
            ## if len(catalog)%500 == 0:
            ##     print len(catalog)
            # TODO: make some requirement to be included (exclude outliers)
            if len(flags['output_name']) > 0:
                F.write('{0},{1},{2},{3},{4},{5},{6},{7}\n'.format(
                    ID, kind, x, y, P, N0, S, D))


    print 'make_lens_catalog: Clearing memory'
    # clear memory
    memory.clear()

    if len(flags['output_name']) > 0:
        print 'make_lens_catalog: closing file!'
        F.close()

    if len(flags['update_collection']) > 0:
        print 'make_lens_catalog: writing updated collection to', flags['update_collection']

        # TODO: get the other params correct!!!!
        collection_fat = swap.collection.Collection()
        for ID in catalog:
            subject = collection.member[ID]
            atx = subject.annotationhistory['At_X']
            labels_in = list(catalog[ID]['agents_labels'])
            labels_fat = []
            for atx_i in atx:
                labels_fat.append([])
                for atx_ij in atx_i:
                    labels_fat[-1].append(labels_in.pop(0))
            subject.annotationhistory.update({'labels': labels_fat})
            collection_fat.member.update({ID: subject})
        swap.write_pickle(collection_fat, flags['update_collection'])

    print 'make_lens_catalog: All done!'

    return catalog

# ======================================================================

if __name__ == '__main__':
    # do argparse style; I find this /much/ easier than getopt (sorry Phil!)
    import argparse
    parser = argparse.ArgumentParser(description=make_lens_catalog.__doc__)
    # Options we can configure
    parser.add_argument("--image_y_size",
                        action="store",
                        dest="image_y_size",
                        type=int,
                        default=440,
                        help="Specify the y coordinate size of the image. Used for converting between database and catalog coordinate conventions.")
    parser.add_argument("--output_directory",
                        action="store",
                        dest="output_directory",
                        default="./",
                        help="Output directory for catalogs.")
    parser.add_argument("--update_collection",
                        action="store",
                        dest="update_collection",
                        default="",
                        help="Create updated catalog.")
    parser.add_argument("--output_name",
                        action="store",
                        dest="output_name",
                        default="catalog.dat",
                        help="Output name for catalogs.")
    parser.add_argument("--skill",
                        action="store_true",
                        dest="skill",
                        default=False,
                        help="Weight by skill. Currently not implimented (but in the future!)")
    parser.add_argument("--catalog_path",
                        action="store",
                        dest="catalog_path",
                        default="",
                        help="Path to catalog data file we start from.")
    # Required args
    parser.add_argument("collection_path",
                        help="Path to collection data file.")
    options = parser.parse_args()
    args = vars(options)
    catalog = make_lens_catalog(args)
    #make_lens_catalog(sys.argv[1:])

# ======================================================================
