#!/usr/bin/env python
# ======================================================================

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

import swap

from scipy import ndimage
from os import path
from urllib import FancyURLopener

# ======================================================================


# the fancy way of scraping images from the web; you gotta pretend you are a browser
class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
myopener = MyOpener()

# ======================================================================

def get_online_png(url, outname=None):
    fname = url.split('/')[-1]
    if not outname:
        outname = fname

    # download file if we don't already have it
    if not path.exists(outname):
        F = myopener.retrieve(url, outname)
    else:
        F = [outname]
    I = ndimage.imread(F[0]) / 255.
    return I

def pdf2d(ax, ay, xbins=51, ybins=51,
          weights=None, smooth=0, color='b', style='contour',
          axis=None):

    try:
        plt.xlim([xbins[0], xbins[-1]])
    except TypeError:
        plt.xlim(ax.min(), ax.max())
    try:
        plt.ylim([ybins[0], ybins[-1]])
    except TypeError:
        plt.ylim(ay.min(), ay.max())

    # npts = int((ax.size/4)**0.5)
    H, x, y = np.histogram2d(ax, ay, weights=weights, bins=[xbins, ybins])

    try:
        extent = (xbins[0], xbins[-1], ybins[0], ybins[-1])
    except TypeError:
        extent = (ax.min(), ax.max(), ay.min(), ay.max())

    if ('contour' in style) + ('shaded' in style):
        contour_hist(H, extent, smooth, color, style, axis)

    if 'points' in style:
        if axis != None:
            axis.scatter(ax, ay, c=color, marker='o', alpha=0.25)
        else:
            plt.scatter(ax, ay, c=color, marker='o', alpha=0.25)
    # endif

    if 'hist' in style:
        if axis != None:
            axis.imshow(H.T, extent=extent)
        else:
            plt.imshow(H.T, extent=extent)

    return

# Taken from pappy/plotting.py, does 2d contours pretty well
def contour_hist(H, extent=None,
          smooth=0, color='b', style='contour',
          axis=None):

    # Smooth the histogram into a PDF:
    if smooth > 0:
        H = ndimage.gaussian_filter(H, smooth)

    norm = numpy.sum(H.flatten())
    H = H * (norm > 0.0) / (norm + (norm == 0.0))

    sortH = numpy.sort(H.flatten())
    cumH = sortH.cumsum()
    # 1, 2, 3-sigma, for the old school:
    lvl00 = 2*sortH.max()
    lvl68 = sortH[cumH>cumH.max()*0.32].min()
    lvl95 = sortH[cumH>cumH.max()*0.05].min()
    lvl997 = sortH[cumH>cumH.max()*0.003].min()

    #   print "2D histogram: min,max = ",H.min(),H.max()
    #   print "Contour levels: ",[lvl00,lvl68,lvl95,lvl997]

    if 'shaded' in style:

        # Plot shaded areas first:
        if axis != None:
            axis.contourf(H.T, [lvl997, lvl95], colors=color, alpha=0.1,
                           extent=extent)
            axis.contourf(H.T, [lvl95, lvl68], colors=color, alpha=0.4,
                           extent=extent)
            axis.contourf(H.T, [lvl68, lvl00], colors=color, alpha=0.9,
                           extent=extent)

        else:
            plt.contourf(H.T, [lvl997, lvl95], colors=color, alpha=0.1,
                           extent=extent)
            plt.contourf(H.T, [lvl95, lvl68], colors=color, alpha=0.4,
                           extent=extent)
            plt.contourf(H.T, [lvl68, lvl00], colors=color, alpha=0.9,
                           extent=extent)

    if 'contour' in style:
        if axis != None:
            axis.contour(H.T, [lvl68, lvl95, lvl997], colors=color,
                               extent=extent)
        else:
            plt.contour(H.T, [lvl68, lvl95, lvl997], colors=color,
                               extent=extent)
        #   plt.contour(H.T, [lvl68, lvl95], colors=color,
        #                      extent=extent)

    return

# ======================================================================

def make_lens_atlas(argv):
    """
    NAME
        make_lens_atlas

    PURPOSE
        Given location of bureau and collection pickles as well as a list of
        subjects, this script produces a set of annotated images of lenses
        (heatmaps for lens locations, markers for where clicks were, etc).

    COMMENTS
        You have to download the file so it chooses whever your output
        directory is to also download the raw images.
        This should be pretty customizable.

    FLAGS
        -h              Print this message
        --heatmap       Do heatmaps
        --contour       Do contours
        --field         Do full image
        --stamp         Do cutouts
        --alpha         Do alpha

        --points N      Take N agents and plot them. Any number < 0 = do all
        --skill         Weight agent markers by skill

    INPUTS
        bureau.pickle
        collection.pickle
        catalog.dat
            Assumed format:
            ID   kind   x   y    P     N0   S

            Here:
            ID = Space Warps subject ID
            kind = Space Warps subject type (sim, dud, test)
            x,y = object (cluster) centroid, in pixels
            P = Space Warps subject probability
            N0 = number of markers in the cluster
            S = total skill per cluster, summed over markers

    OUTPUTS

    EXAMPLE

    BUGS

    AUTHORS
        This file is part of the Space Warps project, and is distributed
        under the GPL v2 by the Space Warps Science Team.
        http://spacewarps.org/

    HISTORY
        2013-07-16  started Davis (KIPAC)
    """

    # ------------------------------------------------------------------
    # Some constants:

    output_directory = './'
    stamp_size = 50
    xbins = np.arange(stamp_size * 2)
    ybins = np.arange(stamp_size * 2)
    dtype_catalog = {'names': ('ID', 'kind', 'x', 'y', 'P', 'N0', 'S'),
                   'formats': (np.str, np.str, np.float, np.float,
                               np.float, np.float, np.float)}

    smooth_click = 3
    figsize_stamp = (5, 5)
    figsize_field = (15, 15)

    # ------------------------------------------------------------------
    # Read in options:

    try:
        opts, args = getopt.getopt(argv,"h",
                ["help", "heatmap", "contour", "field", "stamp", "alpha",
                 "points", "skill"])
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        print make_lens_atlas.__doc__  # will print the big comment above.
        return

    flags = {'points': 30,
             'heatmap': True,
             'contour': True,
             'field': True,
             'stamp': True,
             'alpha': True,
             'skill': True,
            }

    for o,a in opts:
        if o in ("-h", "--help"):
            print make_lens_atlas.__doc__
            return
        elif o in ("--heatmap"):
            flags['heatmap'] = True
        elif o in ("--contour"):
            flags['contour'] = True
        elif o in ("--field"):
            flags['field'] = True
        elif o in ("--stamp"):
            flags['stamp'] = True
        elif o in ("--alpha"):
            flags['alpha'] = True
        elif o in ("--skill"):
            flags['skill'] = True
        elif o in ("--points"):
            flags['points'] = int(a)
        else:
            assert False, "unhandled option"

    # Check for pickles in array args:
    if len(args) == 2:
        #bureau_path = args[0]
        collection_path = args[0]
        catalog_path = args[1]
        print "make_lens_atlas: illustrating behaviour captured in bureau, collection, and lens files: "
        #print "make_lens_atlas: ", bureau_path
        print "make_lens_atlas: ", collection_path
        print "make_lens_atlas: ", catalog_path
    else:
        print make_lens_atlas.__doc__
        return

    # ------------------------------------------------------------------
    # Read in files:

    #bureau = swap.read_pickle(bureau_path, 'bureau')  # TODO: needed?
    collection = swap.read_pickle(collection_path, 'collection')
    catalog = np.loadtxt(catalog_path, dtype=dtype_catalog)

    #print "make_lens_atlas: bureau numbers ", len(bureau.list())
    print "make_lens_atlas: collection numbers ", len(collection.list())
    print "make_lens_atlas: catalog numbers ", len(catalog)

    # ------------------------------------------------------------------
    # Run through data:

    # ------------------------------------------------------------------
    # Stamps:
    if flags['stamp']:
        print "make_lens_atlas: running stamps"
        for lens_i in range(len(catalog)):
            ID = catalog[lens_i, 0]
            x = catalog[lens_i, 2]
            y = catalog[lens_i, 3]
            subject = collection.member[ID]
            annotationhistory = subject.annotationhistory

            # ------------------------------------------------------------------
            # download png
            url = subject.location
            outname = output_directory + '{0}_field.png'.format(ID)
            im = get_online_png(url, outname)
            min_x = np.int(np.max((x - stamp_size, 0)))
            max_x = np.int(np.min((x + stamp_size, im.shape[0])))
            min_y = np.int(np.max((y - stamp_size, 0)))
            max_y = np.int(np.min((y + stamp_size, im.shape[1])))

            if (min_x >= max_x) + (min_y >= max_y):
                print "make_lens_atlas: misshapen lens for ID ", ID
                continue

            # if it is a training image, claim the alpha parameter
            if im.shape[2] == 4:
                alpha = im[:, :, 3][min_y: max_y, min_x: max_x]
                im = im[:, :, :3][min_y: max_y, min_x: max_x]
            else:
                alpha = None
                im = im[min_y: max_y, min_x: max_x]

            if (flags['contour']) + (flags['heatmap']):

                itwas = annotationhistory['ItWas']
                x_all = annotationhistory['At_X']
                y_all = annotationhistory['At_Y']

                x_markers_all = np.array([xi for xj in x_all for xi in xj])
                y_markers_all = np.array([yi for yj in y_all for yi in yj])

                # now filter markers by those that are within
                # stamp_size of the stamp
                agents_numbers = np.arange(
                        x_markers_all.size)
                conds = ((x_markers_all >= min_x) * (x_markers_all <= max_x) *
                         (y_markers_all >= min_y) * (y_markers_all <= max_y))
                agents = agents_numbers[conds]

                x_markers = x_markers_all[agents]
                y_markers = y_markers_all[agents]

                # filter markers
                n_catalog = len(annotationhistory['Name'])
                if (flags['points'] >= 0) * \
                        (flags['points'] < n_catalog):
                    agents_points = np.random.choice(
                            agents,
                            size=flags['points'], replace=False)
                else:
                    agents_points = agents
                x_markers_filtered = x_markers_all[agents_points]
                y_markers_filtered = y_markers_all[agents_points]

                if flags['skill']:
                    PL_all = annotationhistory['PL']
                    PD_all = annotationhistory['PD']

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

                    skill_all = swap.expectedInformationGain(0.5, PL, PD)
                    skill = skill[agents]

                    smax = 100
                    smin = 5
                    sizes_all = (skill_all - np.min(skill)) * (smax - smin) / \
                            (np.max(skill) - np.min(skill))
                    sizes_filtered = sizes_all[agents_points]
                    colors = [(0, 1.0, 0) for i in x_markers_filtered]
                else:
                    skill = None
                    sizes_filtered = 50
                    colors = (0, 1.0, 0)

                # ----------------------------------------------------------
                # contours
                if flags['contour']:
                    fig = plt.figure(figsize=figsize_stamp)
                    ax = fig.add_subplot(111)
                    ax.imshow(im)

                    # plot points
                    if flags['points'] > 0:
                        ax.scatter(x_markers_filtered - min_x,
                                   y_markers_filtered - min_y,
                                   c=colors, s=sizes_filtered,
                                   alpha=0.25)

                    # now do the lens locations
                    # don't need to filter the x's since that is filtered by
                    # xbins and ybins anyways
                    pdf2d(x_markers - min_x, y_markers - min_y,
                          xbins=xbins, ybins=ybins,
                          weights=skill, smooth=smooth_click,
                          color=(0, 1.0, 0),
                          style='contour',
                          axis=ax)

                    if flags['alpha'] * (alpha != None):
                        contour_hist(alpha.T,
                            extent=(xbins[0], xbins[-1], ybins[0], ybins[-1]),
                            color='w', style='contour', axis=ax)

                    ax.tick_params(\
                        axis='both',          # changes apply to the x-axis
                        which='both',      # both major and minor ticks are affected
                        bottom='off',      # ticks along the bottom edge are off
                        top='off',         # ticks along the top edge are off
                        left='off',
                        right='off',
                        labelleft='off',
                        labelbottom='off') # labels along the bottom edge are off

                    fig.savefig(output_directory +
                                '{0}_cluster_{1}_contour.pdf'.format(
                                    ID, lens_i))

                # ----------------------------------------------------------
                # heatmaps
                if flags['heatmap']:
                    fig = plt.figure(figsize=figsize_stamp)
                    ax = fig.add_subplot(111)

                    # now do the lens locations
                    # don't need to filter the x's since that is filtered by
                    # xbins and ybins anyways
                    pdf2d(x_markers - min_x, y_markers - min_y,
                          xbins=xbins, ybins=ybins,
                          weights=skill, smooth=smooth_click,
                          color=(0, 1.0, 0),
                          style='hist',
                          axis=ax)

                    if flags['alpha'] * (alpha != None):
                        contour_hist(alpha.T,
                            extent=(xbins[0], xbins[-1], ybins[0], ybins[-1]),
                            color='w', style='contour', axis=ax)

                    ax.tick_params(\
                        axis='both',          # changes apply to the x-axis
                        which='both',      # both major and minor ticks are affected
                        bottom='off',      # ticks along the bottom edge are off
                        top='off',         # ticks along the top edge are off
                        left='off',
                        right='off',
                        labelleft='off',
                        labelbottom='off') # labels along the bottom edge are off

                    fig.savefig(output_directory +
                                '{0}_cluster_{1}_heatmap.pdf'.format(
                                    ID, lens_i))

    # ------------------------------------------------------------------
    # Fields
    if flags['field']:
        print "make_lens_atlas: running fields"
        # find the unique IDs. mark centers and also centrals if clustering is
        # done
        unique_IDs = np.unique(catalog[:, 0])
        for ID in unique_IDs:
            mini_catalog = catalog[catalog[:, 0] == ID]
            subject = collection.member[ID]
            annotationhistory = subject.annotationhistory

            # ------------------------------------------------------------------
            # download png
            url = subject.location
            outname = output_directory + '{0}_field.png'.format(ID)
            im = get_online_png(url, outname)

            # if it is a training image, claim the alpha parameter
            if im.shape[2] == 4:
                alpha = im[:, :, 3]
                im = im[:, :, :3]
            else:
                alpha = None

            fig = plt.figure(figsize=figsize_field)
            ax = fig.add_subplot(111)
            ax.imshow(im)
            xbins = np.arange(im.shape[0])
            ybins = np.arange(im.shape[1])
            min_x = 0
            min_y = 0
            max_x = im.shape[0]
            max_y = im.shape[1]

            # plot cluster centers
            x_centers = mini_catalog[:, 2]
            y_centers = mini_catalog[:, 3]
            skill_centers = mini_catalog[:, 6]
            colors_centers = [(0, 1.0, 0) for i in x_centers]

            if flags['skill']:
                sizes_centers = (
                        (skill_centers - np.min(skill_centers)) *
                        (200 - 10) /
                        (np.max(skill_centers) - np.min(skill_centers)))
            else:
                sizes_centers = [100 for i in x_centers]
            ax.scatter(x_centers, y_centers,
                       marker='d', c=colors_centers,
                       s=sizes_centers, alpha=0.25)

            itwas = annotationhistory['ItWas']
            x_all = annotationhistory['At_X']
            y_all = annotationhistory['At_Y']

            x_markers_all = np.array([xi for xj in x_all for xi in xj])
            y_markers_all = np.array([yi for yj in y_all for yi in yj])

            # now filter markers by those that are within
            # stamp_size of the stamp
            agents_numbers = np.arange(
                    x_markers_all.size)
            conds = ((x_markers_all >= min_x) * (x_markers_all <= max_x) *
                     (y_markers_all >= min_y) * (y_markers_all <= max_y))
            agents = agents_numbers[conds]

            x_markers = x_markers_all[agents]
            y_markers = y_markers_all[agents]

            # filter markers
            n_catalog = len(annotationhistory['Name'])
            if (flags['points'] >= 0) * \
                    (flags['points'] < n_catalog):
                agents_points = np.random.choice(
                        agents,
                        size=flags['points'], replace=False)
            else:
                agents_points = agents
            x_markers_filtered = x_markers_all[agents_points]
            y_markers_filtered = y_markers_all[agents_points]

            if flags['skill']:
                PL_all = annotationhistory['PL']
                PD_all = annotationhistory['PD']

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

                skill_all = swap.expectedInformationGain(0.5, PL, PD)
                skill = skill[agents]

                smax = 100
                smin = 5
                sizes_all = (skill_all - np.min(skill)) * (smax - smin) / \
                        (np.max(skill) - np.min(skill))
                sizes_filtered = sizes_all[agents_points]
                colors = [(0, 1.0, 0) for i in x_markers_filtered]
            else:
                skill = None
                sizes_filtered = 50
                colors = (0, 1.0, 0)

            # ----------------------------------------------------------
            # contours
            if flags['contour']:

                # now do the lens locations
                # don't need to filter the x's since that is filtered by
                # xbins and ybins anyways
                pdf2d(x_markers - min_x, y_markers - min_y,
                      xbins=xbins, ybins=ybins,
                      weights=skill, smooth=smooth_click,
                      color=(0, 1.0, 0),
                      style='contour',
                      axis=ax)

            # ----------------------------------------------------------
            # plot points
            if flags['points'] > 0:
                ax.scatter(x_markers_filtered - min_x,
                           y_markers_filtered - min_y,
                           c=colors, s=sizes_filtered,
                           alpha=0.25)

            # ----------------------------------------------------------
            # do alpha
            if flags['alpha'] * (alpha != None):
                contour_hist(alpha.T,
                    extent=(xbins[0], xbins[-1], ybins[0], ybins[-1]),
                    color='w', style='contour', axis=ax)


            ax.tick_params(\
                axis='both',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom='off',      # ticks along the bottom edge are off
                top='off',         # ticks along the top edge are off
                left='off',
                right='off',
                labelleft='off',
                labelbottom='off') # labels along the bottom edge are off

            fig.savefig(output_directory + '{0}_field.pdf'.format(ID))

# ======================================================================

if __name__ == '__main__':
    make_lens_atlas(sys.argv[1:])

# ======================================================================
