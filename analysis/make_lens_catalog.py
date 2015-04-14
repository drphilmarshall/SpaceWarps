"""
File: make_lens_catalog.py
Author: Chris Davis
Description: Given database information, creates the cluster catalog and downloads fields and cutouts.

"""

from __future__ import print_function, division

import sys, getopt, numpy as np

import matplotlib
# Force matplotlib to not use any Xwindows backend:
matplotlib.use('Agg')

# Fonts, latex:
matplotlib.rc('font', **{'family':'serif', 'serif':['TimesNewRoman']})
matplotlib.rc('text', usetex=True)

from matplotlib import pyplot as plt

bfs, sfs = 20, 16
params = { 'axes.labelsize': bfs,
            'text.fontsize': bfs,
          'legend.fontsize': bfs,
          'xtick.labelsize': sfs,
          'ytick.labelsize': sfs}
plt.rcParams.update(params)

origin = 'lower'

import numpy as np
import pandas as pd
from urllib import FancyURLopener
from scipy.ndimage import imread
from scipy.misc import imsave
from os import path, makedirs
from ast import literal_eval

# ======================================================================
# Some parameter definitions. Can config catalog properties here or in the
# functions...
# ======================================================================

collection_categories = ['ID', 'ZooID', 'location', 'mean_probability', 'category', 'kind', 'flavor', 'state', 'status', 'truth', 'stage']
annotation_categories = ['At_X', 'At_Y', 'PD', 'PL', 'ItWas']
cluster_catalog_labels = ['object_id', 'x', 'y', 'markers_in_object', 'skill_sum', 'markers_in_field', 'people_marking_objects', 'people_marking_field', 'people_looking_at_field', 'object_size']
field_size = 440
# eps is largely determined by looking at the distribution of dispersion values
# as well as looking at actual images to get a rough sense of the tradeoff
# between accidentally misclassifying a large object as multiple and
# multiple objects as one
eps = 30#48
min_samples = 3#2
stamp_size = 96
convert_outliers = False#True

# ======================================================================

def augment_catalog(catalog, cluster_directory, augmented_directory):
    """Routine for augmenting an existent catalog

    Parameters
    ----------
    catalog : dataframe
        Catalog of all the cluster images.

    cluster_directory : path
        Location of the directory containing the cluster images.

    augmented_directory : path
        Location of the directory where the augmented data will be saved.

    Returns
    -------
    augmented_catalog : dataframe
        Takes the cluster_catalog and applies several affine transformations.

    Notes
    -----
    augmentation type: 0-3 are 90 degree rotations, 4-7 are 90 rotations plus flip

    """

    augmented_catalog = []
    augmented_catalog_columns = list(catalog.columns) + ['stamp_id', 'stamp_name', 'augment_type']
    for cati in catalog.iterrows():
        entry = cati[1]
        image_path = cluster_directory + entry['object_name']
        image = imread(image_path)
        augmented_images = augment_image(image)
        for ai, augmented_image in enumerate(augmented_images):
            stamp_id = entry['object_id'] + len(catalog) * ai
            stamp_name = '{2}_{1}_{0}.png'.format(entry['ZooID'],
                                                  entry['object_id'],
                                                  stamp_id)
            augment_type = ai
            augmented_entry = np.append(entry.values,
                                        [stamp_id, stamp_name, augment_type])
            augmented_catalog.append(augmented_entry)
            # save augmented image
            imsave(augmented_directory + stamp_name, augmented_image)
    augmented_catalog = pd.DataFrame(augmented_catalog,
                                     columns=augmented_catalog_columns)

    return augmented_catalog

def augment_image(image):
    """Do all combinations of rotations and flips

    Parameters
    ----------
    image : HxWxC array

    Returns
    -------
    augmented_images : list of images
        Eight images in total, for each combination of flip and rot90.

    """
    augmented_images = []
    for do_flip in [False, True]:
        for k in [0, 1, 2, 3]:
            augmented_image = np.rot90(image, k=k)
            if do_flip:
                augmented_image = augmented_image[:, ::-1, :]
            augmented_images.append(augmented_image)
    return augmented_images

def create_cluster_catalog_and_cutouts(collection,
        field_directory, cluster_directory,
        knownlens=None,
        eps=eps, min_samples=min_samples,
        convert_outliers=convert_outliers,
        do_a_few=None):
    """Main routine for creating the cluster catalog.

    Parameters
    ----------
    collection : dataframe of swap objects.
        Contains collection_categories and annotation_categories

    knownlens : pandas dataframe

    Returns
    -------
    catalog : cluster catalog with the following columns

    Notes
    -----


    """

    # create cluster catalog from collection
    print('creating incomplete cluster catalog')
    catalog = create_incomplete_cluster_catalog(collection,
        eps=eps, min_samples=min_samples,
        convert_outliers=convert_outliers,
        do_a_few=do_a_few)
    print('incomplete cluster catalog created!')

    # update the cluster catalog with some file information
    field_names = []
    cluster_names = []
    for cati in catalog.iterrows():
        entry = cati[1]
        field_names.append('{0}.png'.format(entry['ZooID']))
        cluster_names.append('{1}_{0}.png'.format(entry['ZooID'],
                                                  entry['object_id']))
    catalog['field_name'] = field_names
    catalog['object_name'] = cluster_names

    # now download and create the cutouts
    # make sure these paths exist!
    alphas = create_cluster_cutouts(catalog,
        field_directory, cluster_directory, stamp_size=stamp_size)
    print('cluster cutouts created!')

    # alphas
    cluster_types = []
    for cati in catalog.iterrows():
        cati, entry = cati
        alpha = alphas[cati]
        field_flavor = entry['field_flavor']
        if 'lens' in field_flavor:
            if alpha == 1:
                cluster_type = 'simulated ' + field_flavor
            else:
                cluster_type = 'dud'
        elif 'test' in field_flavor:
            cluster_type = 'unknown'
        elif 'dud' in field_flavor:
            cluster_type = 'dud'
        else:
            raise Exception('Unrecognized field_flavor {0}'.format(field_flavor))
        cluster_types.append(cluster_type)
    print('alphas done')

    # knownlens
    # cludgey way to ensure we have the item
    if type(knownlens) != type(None):
        catalog_zooid_index = catalog.index
        catalog_zooid = catalog.set_index(['ZooID'])
        catalog_zooid['index'] = catalog_zooid_index
        for kl in knownlens.iterrows():
            x = kl[1]['x']
            y = 440 - kl[1]['y']
            zooid = kl[1]['ZooID']
            if zooid in catalog_zooid.index:
                cci = catalog_zooid.loc[zooid]
                ccx = cci['x']
                ccy = cci['y']
                l2 = np.square(x - ccx) + np.square(y - ccy)
                if type(l2) == np.float64:
                    index = cci['index']
                    cluster_types[index] = 'known lens'
                elif type(l2) != np.float64:
                    index = cci['index'][np.argmin(l2.values)]
                    cluster_types[index] = 'known lens'
        print('known lens done!')

    catalog['object_flavor'] = cluster_types

    return catalog

def create_incomplete_cluster_catalog(catalog,
                                      stamp_size=stamp_size,
                                      field_size_x=field_size,
                                      field_size_y=field_size,
                                      eps=eps, min_samples=min_samples,
                                      convert_outliers=convert_outliers,
                                      do_a_few=None):
    """Creates clustering catalog just based off of swap user clicks.

    Parameters
    ----------
    catalog : dataframe
        Contains collection_ and annotation_categories

    stamp_size : int, optional
        How big an image are we looking to make?

    field_size_x, field_size_y : int, optional
        How big are the fields we are extracting stamps from?

    eps, min_samples, convert_outliers : config parameters for outlier_clusters_dbscan

    Returns
    -------
    cluster_catalog : another dataframe
        Catalog with all the cluster entries.

    Notes
    -----
    I call this 'incomplete' because it does not have the full information I
    would like to have in the cluster catalog: things like whether the cutout
    contains a knownlens or is a bonafide training simulation cutout.

    """

    cluster_catalog = []
    cluster_id = 0
    # step through the objects in catalog
    # TODO: remove this small sampling thing
    if do_a_few:
        cat_list = np.random.choice(len(catalog), size=do_a_few)
    else:
        cat_list = xrange(len(catalog))
    for cati in cat_list:

        # get markers. The literal_eval is because the catalog entries are strings.
        x_unflat = literal_eval(catalog['At_X'][cati])
        y_unflat = literal_eval(catalog['At_Y'][cati])
        # flatten out x and y. also cut out empty entries
        x = np.array([xi for xj in x_unflat for xi in xj])
        y = np.array([yi for yj in y_unflat for yi in yj])
        did_mark = np.array([True if len(xj) > 0 else False for xj in x_unflat])
        users = np.array([xj for xj in xrange(len(x_unflat))
                          for xi in x_unflat[xj]])
        total_marked_looks = np.sum(did_mark)
        total_looks = len(x_unflat)

        # repeat for PD and PL = proxies for weight
        PL_everyone = literal_eval(catalog['PL'][cati])
        PL_unflat = []
        PD_everyone = literal_eval(catalog['PD'][cati])
        PD_unflat = []
        for i, xj in enumerate(x_unflat):
            # len(xj) of empty = 0
            PL_unflat.append([PL_everyone[i]] * len(xj))
            PD_unflat.append([PD_everyone[i]] * len(xj))

        PL = np.array([PLi for PLj in PL_unflat for PLi in PLj])
        PD = np.array([PDi for PDj in PD_unflat for PDi in PDj])
        skill = expectedInformationGain(0.5, PL, PD)

        # create weights
        # if a user clicks multiple times, downweight by that fraction
        binusers = np.bincount(users)
        w = 1. / binusers[users]

        # TODO: weight by skill?

        # cluster
        cluster_centers, cluster_labels, labels = \
            outlier_clusters_dbscan(x, y, w=w, eps=eps, min_samples=min_samples)

        # add to catalog
        for cluster_label_i, cluster_label in enumerate(cluster_labels):

            cluster_center = cluster_centers[cluster_label_i]
            x_i, y_i = cluster_center

            if np.int(np.ceil(x_i - stamp_size / 2)) >= field_size_x:
                print('Mislabled cluster? {0} {1} {2} {3}'.format(
                    cati, cluster_label_i, x_i, y_i))
                continue
            elif np.int(np.ceil(y_i - stamp_size / 2)) >= field_size_y:
                print('Mislabled cluster? {0} {1} {2} {3}'.format(
                    cati, cluster_label_i, x_i, y_i))
                continue
            elif np.int(np.floor(x_i + stamp_size / 2)) < 0:
                print('Mislabled cluster? {0} {1} {2} {3}'.format(
                    cati, cluster_label_i, x_i, y_i))
                continue
            elif np.int(np.floor(y_i + stamp_size / 2)) < 0:
                print('Mislabled cluster? {0} {1} {2} {3}'.format(
                    cati, cluster_label_i, x_i, y_i))
                continue

            members = (labels == cluster_label)  # array of booleans

            N0 = np.sum(members)
            S = np.sum(skill[members])
            Ntot = len(members)

            cluster_marked_looks = len(np.unique(users[members]))

            dispersion = np.sqrt(np.mean(np.square(x_i - x[members]) +
                                         np.square(y_i - y[members])))

            cluster_catalog_i = [catalog[category][cati] for category
                                 in collection_categories]
            # now add to the entry the things we learned about the cluster
            cluster_catalog_i += [cluster_id, x_i, y_i, N0, S, Ntot, cluster_marked_looks, total_marked_looks, total_looks, dispersion]
            cluster_catalog.append(cluster_catalog_i)
            cluster_id += 1

    cluster_catalog = pd.DataFrame(cluster_catalog, columns=collection_categories + cluster_catalog_labels)

    # we now rename one of the cluster_catalog columns
    cluster_catalog.rename(columns={'flavor': 'field_flavor'}, inplace=True)

    return cluster_catalog

def create_cluster_cutouts(catalog, field_directory, cluster_directory,
                           stamp_size=stamp_size):
    """Take a cluster catalog, download field and stamps
    """
    alphas = np.zeros(len(catalog))
    for clusteri in xrange(len(catalog)):
        # define the outputs for the images
        outname_field = field_directory + catalog['field_name'][clusteri]
        outname_cluster = cluster_directory + catalog['object_name'][clusteri]

        # get the centers
        x = catalog['x'][clusteri]
        y = catalog['y'][clusteri]

        # download the field
        im = get_online_png(catalog['location'][clusteri], outname_field)

        # create the stamp
        min_x = np.int(np.floor(x - stamp_size / 2))
        max_x = np.int(np.ceil(x + stamp_size / 2))
        min_y = np.int(np.floor(y - stamp_size / 2))
        max_y = np.int(np.ceil(y + stamp_size / 2))
        pad_min_x = 0
        pad_max_x = 0
        pad_min_y = 0
        pad_max_y = 0
        pad_trip = False
        if min_x < 0:
            pad_min_x = -min_x
            min_x = 0
            pad_trip = True
        if max_x >= im.shape[1]:
            pad_max_x = max_x - im.shape[1]
            max_x = im.shape[1]
            pad_trip = True
        if min_y < 0:
            pad_min_y = -min_y
            min_y = 0
            pad_trip = True
        if max_y >= im.shape[0]:
            pad_max_y = max_y - im.shape[0]
            max_y = im.shape[0]
            pad_trip = True

        im_cut = np.pad(im[min_y: max_y, min_x: max_x],
                        ((pad_min_y, pad_max_y), (pad_min_x, pad_max_x), (0, 0)),
                        mode='constant')
        im_cut = im_cut[:stamp_size, :stamp_size]

        # now check if the center is in a high alpha region (if alpha is included, as it is with training)
        if im.shape[2] == 4:
            im_mask = im_cut[:, :, 3].copy()
            im_cut = im_cut[:, :, :3]

            # # for some reason the numbers are not obviously formatted...
            # im_mask -= im_mask.mean()
            # im_mask /= im_mask.std()
            # im_mask[im_mask < 5] = 0
            # im_mask[im_mask >= 5] = 1

            if np.any(im_mask > 254 / 255.):
                alphas[clusteri] = 1

        imsave(outname_cluster, im_cut)

    return alphas

def convert_swap_collection_to_dataframe(collection, stage,
        collection_categories=collection_categories,
        annotation_categories=annotation_categories):
    """

    Parameters
    ----------
    collection : swap object

    stage : string
        Stage of the swap object

    collection_categories : list of strings
        Columns in the subjects that we want to collect.

    annotation_categories : list of strings
        Columns in the subjects's annotationhistory that we want to collect.

    Returns
    -------
    catalog : pandas dataframe

    Notes
    -----
    ('category', array(['test', 'training'], dtype=object))
    ('kind', array(['dud', 'sim', 'test'], dtype=object))
    ('flavor', array(['dud', u'lensed galaxy', u'lensed quasar',
                      u'lensing cluster','test'], dtype=object))
    ('state', array(['active', 'inactive'], dtype=object))
    ('status', array(['detected', 'rejected', 'undecided'], dtype=object))
    ('truth', array(['LENS', 'NOT', 'UNKNOWN'], dtype=object))

    conclusion: only need flavor, status

    """

    catalog = []
    for ID in collection.list():

        subject = collection.member[ID]
        catalog_i = []

        # flatten out x and y.
        annotationhistory = subject.annotationhistory
        x_unflat = annotationhistory['At_X']  # list of lists of clicks
        x = np.array([xi for xj in x_unflat for xi in xj])

        # cut out entries with no clicks
        if len(x) < 1:
            continue
        # oh yeah there's that absolutely nutso entry with 50k clicks. I think
        # it was the first training image? So everyone saw it. . . .
        if len(x) > 10000:
            continue

        for category in collection_categories:
            if category == 'stage':
                catalog_i.append(stage)
            else:
                catalog_i.append(subject.__dict__[category])
        for category in annotation_categories:
            catalog_i.append(list(annotationhistory[category]))

        catalog.append(catalog_i)
    # convert catalog to a dataframe
    catalog = pd.DataFrame(catalog, columns=collection_categories + annotation_categories)

    return catalog

def shannon(x):
    if isinstance(x, np.ndarray) == False:

        if x>0:
            res = x*np.log2(x)
        else:
            res = 0.0

    else:
        x[x == 0] = 1.0
        res = x*np.log2(x)

    return res

def expectedInformationGain(p0, M_ll, M_nn):
    p1 = 1-p0

    I =   p0 * (shannon(M_ll) + shannon(1-M_ll)) \
        + p1 * (shannon(M_nn) + shannon(1-M_nn)) \
        - shannon(M_ll*p0 + (1-M_nn)*p1) \
        - shannon((1-M_ll)*p0 + M_nn*p1)

    return I

def outlier_clusters_dbscan(x, y, w=None,
                            eps=eps, min_samples=min_samples,
                            convert_outliers=convert_outliers):
    """
    Parameters
    ----------
    x, y : lists of floats
        The x and y axis locations of each click.

    eps : float, optional
        The maximum distance between two samples for them to be considered
        as in the same neighborhood.
    min_samples : int, optional
        The number of samples in a neighborhood for a point to be considered
        as a core point.

    convert_outliers : binary, optional
        DBSCAN assigns outliers a cluster label -1. This says take each -1 and
        give it a unique positive value. Every click then becomes a cluster.

    Returns
    -------
    cluster_centers : array
        Each entry in cluster_centers is the center of that cluster

    cluster_labels : array
        The i-th cluster_center has label cluster_labels[i]

    labels : array
        The labels of all the points.

    Notes
    -----
    http://en.wikipedia.org/wiki/DBSCAN is a useful reference!
    Here is what wikipedia says about the algorithm:

    DBSCAN requires two parameters: eps and the minimum number of points
    required to form a dense region[a] (min_samples). It starts with an
    arbitrary starting point that has not been visited. This point's
    eps-neighborhood is retrieved, and if it contains sufficiently many points,
    a cluster is started. Otherwise, the point is labeled as noise. Note that
    this point might later be found in a sufficiently sized eps-environment of
    a different point and hence be made part of a cluster.

    If a point is found to be a dense part of a cluster, its eps-neighborhood
    is also part of that cluster. Hence, all points that are found within the
    eps-neighborhood are added, as is their own eps-neighborhood when they are
    also dense. This process continues until the density-connected cluster is
    completely found. Then, a new unvisited point is retrieved and processed,
    leading to the discovery of a further cluster or noise.
    """
    from sklearn.cluster import DBSCAN
    from sklearn.metrics import pairwise_distances

    data = np.vstack((x, y)).T

    if len(data) < min_samples:
        #print('clustering: only 1 data point!')
        #print('clustering: clustering {0} points, which is fewer than the minimum number of points {1}!'.format(len(data), min_samples))
        cluster_centers = np.array([[-1, -1]])
        cluster_labels = []
        labels = np.array([])

    else:

        clusterer = DBSCAN(eps=eps, min_samples=min_samples)
        db = clusterer.fit(data, sample_weight=w)
        labels = db.labels_
        cluster_labels = list(set(labels))
        if convert_outliers:
            # now step through all the labels and set the -1s each to a new unique label
            label_max = np.max((max(cluster_labels) + 1, 101))
            for label_i, label in enumerate(labels):
                if label == -1:
                    labels[label_i] = label_max
                    label_max += 1
            cluster_labels = list(set(labels))
        else:
            # remove -1 from cluster label definition
            cluster_labels = list(set(labels[labels != -1]))

        # it is possible that I have removed all data!
        if len(labels) == 0:
            #print('clustering: no labels remaining after outlier rejection!')
            cluster_centers = np.array([[-1, -1]])

        else:
            # find the centers of the clusters via mean
            cluster_centers = np.array([np.mean(data[labels == i], axis=0)
                                        for i in cluster_labels])


    return cluster_centers, cluster_labels, labels


# the fancy way of scraping images from the web; you gotta pretend you are a browser
class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

def get_online_png(url, outname, myopener=MyOpener()):
    fname = url.split('/')[-1]

    # download file if we don't already have it
    if not path.exists(outname):
        F = myopener.retrieve(url, outname)
    else:
        # TODO: this is glitched?
        F = [outname]
    try:
        I = imread(F[0]) * 1. / 255
    except Exception as er:
        # this field probably didn't download for *reasons*
        print(F, url, outname)
        try:
            import time
            time.sleep(10)
            I = imread(F[0]) * 1. / 255
        except TypeError as er:

            # okay let's give this another shot
            from os import remove
            remove(outname)
            F = myopener.retrieve(url, outname)
            I = imread(F[0]) * 1. / 255

    return I



if __name__ == '__main__':
    """
    python create_catalogs.py --collection /Users/cpd/Google\ Drive/cs231n/annotated_catalog.csv --knownlens /Users/cpd/Projects/strongcnn/catalog/knownlens.csv --fields /Users/cpd/Desktop/test/fields/ --clusters /Users/cpd/Desktop/test/clusters/ --augment /Users/cpd/Desktop/test/augmented/ --do_a_few 10
    """
    import argparse
    parser = argparse.ArgumentParser(description=create_cluster_catalog_and_cutouts.__doc__)

    # Required args
    parser.add_argument('--collection',
                        action='store',
                        dest='collection',
                        help='Path to annotated catalog used to create clusters and cutouts.')
    parser.add_argument('--knownlens',
                        action='store',
                        dest='knownlens',
                        default=None,
                        help='Path to csv of the knownlens catalog. If none, skips!')
    parser.add_argument('--clusters',
                        action='store',
                        dest='clusters',
                        help='Where are the clusters stored?')
    parser.add_argument('--fields',
                        action='store',
                        dest='fields',
                        default=None,  # can have an empty default!
                        help='Where are we outputting fields? If not specified, defaults to clusters argument.')
    parser.add_argument('--augment',
                        action='store',
                        dest='augment',
                        default=None,
                        help='Where are we outputting augmented results?')
    # Optional args
    parser.add_argument('--do_a_few',
                        action='store',
                        dest='do_a_few',
                        type=int,
                        default=0,
                        help='When greater than 0, do this many entries.')

    options = parser.parse_args()
    options.fields = options.fields if options.fields else options.clusters
    args = vars(options)

    do_a_few = args['do_a_few']
    field_directory = args['fields']
    cluster_directory = args['clusters']
    catalog_path = cluster_directory + '/catalog.csv'
    # make these directories
    if not path.exists(cluster_directory):
        makedirs(cluster_directory)
    if not path.exists(field_directory):
        makedirs(field_directory)

    # load up requisite files
    collection_path = args['collection']
    if '.pickle' in collection_path:
        # will need PJM's swap to interpret the spacewarps database
        try:
            import swap
        except:
            raise Exception('create_catalogs: Unable to import SpaceWarps analysis code!')

        #collection_path = base_collection_path + 'stage{0}'.format(stage) + '/CFHTLS_collection.pickle'
        collection_pickle = swap.read_pickle(collection_path, 'collection')
        stage = -1
        collection = convert_swap_collection_to_dataframe(collection_pickle, stage)
    elif '.csv' in collection_path:
        collection = pd.read_csv(collection_path)
    else:
        raise Exception('create_catalogs: No idea what kind of collection you are giving me here for {0}'.format(collection_path))

    if args['knownlens']:
        knownlens = pd.read_csv(args['knownlens'])
    else:
        knownlens = None

    # create the cluster args
    cluster_args = {'collection': collection,
                    'knownlens': knownlens,
                    'field_directory': field_directory,
                    'cluster_directory': cluster_directory,
                    'do_a_few': do_a_few}

    catalog = create_cluster_catalog_and_cutouts(**cluster_args)
    catalog.to_csv(catalog_path)

    augmented_directory = args['augment']
    if augmented_directory:
        print('create_catalogs: making augmented data!')
        augmented_catalog_path = augmented_directory + '/augmented_catalog.csv'
        if not path.exists(augmented_directory):
            makedirs(augmented_directory)
        augmented_catalog = augment_catalog(catalog, cluster_directory,
                                            augmented_directory)
        augmented_catalog.to_csv(augmented_catalog_path)
