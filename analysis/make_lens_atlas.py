#!/usr/bin/env python
# ======================================================================

# TODO: when pulling points for zoomed, do the clustering as in catalog (should
# be deterministic) so you can filter that way

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

import swap

from scipy.ndimage import gaussian_filter, imread
from os import path
from urllib import FancyURLopener
from matplotlib.mlab import csv2rec

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
    I = imread(F[0]) * 1. / 255
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
            axis.imshow(H.T, extent=extent, cmap=plt.get_cmap('Blues_r'),
                        origin=origin)
        else:
            plt.imshow(H.T, extent=extent, cmap=plt.get_cmap('Blues_r'),
                       origin=origin)

    return

# Taken from pappy/plotting.py, does 2d contours pretty well
def contour_hist(H, extent=None,
          smooth=0, color='b', style='contour',
          axis=None):

    # Smooth the histogram into a PDF:
    if smooth > 0:
        H = gaussian_filter(H, smooth)

    norm = np.sum(H.flatten())
    H = H * (norm > 0.0) / (norm + (norm == 0.0))

    sortH = np.sort(H.flatten())
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

def make_lens_atlas(args):
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
        collection collection.pickle
        catalog catalog.dat
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
        TODO: incorporate some of these defaults into the flags dictionary

    AUTHORS
        This file is part of the Space Warps project, and is distributed
        under the GPL v2 by the Space Warps Science Team.
        http://spacewarps.org/

    HISTORY
        2013-07-16  started Davis (KIPAC)
    """

    # ------------------------------------------------------------------
    # Some defaults:

    flags = {'points': 30,
             'heatmap': False,
             'contour': False,
             'field': False,
             'stamp': False,
             'alpha': False,
             'skill': False,
             'output_directory': './',
             'output_format': 'png',
             'stamp_size': 50,
             'dist_max': 30,
             'stamp_min': 10,
             'smooth_click': 3,
             'figsize_stamp': 5,
             'figsize_field': 10,
             'image_y_size': 440,
            }

    # ------------------------------------------------------------------
    # Read in options:

    # this has to be easier to do...
    for arg in args:
        if arg in flags:
            flags[arg] = args[arg]
        elif arg == 'collection':
            collection_path = args[arg]
        elif arg == 'catalog':
            catalog_path = args[arg]
        else:
            print "make_lens_atlas: unrecognized flag ",arg
    xbins = np.arange(flags['stamp_size'] * 2)
    ybins = np.arange(flags['stamp_size'] * 2)
    figsize_stamp = (flags['figsize_stamp'], flags['figsize_stamp'])
    figsize_field = (flags['figsize_field'], flags['figsize_field'])
    image_y_size = flags['image_y_size']

    print "make_lens_atlas: illustrating behaviour captured in collection, and lens files: "
    print "make_lens_atlas: ", collection_path
    print "make_lens_atlas: ", catalog_path

    ## try:
    ##     opts, args = getopt.getopt(argv,"h",
    ##             ["help", "heatmap=", "contour=", "field=", "stamp=",
    ##              "alpha=", "points=", "skill="])
    ## except getopt.GetoptError, err:
    ##     print str(err) # will print something like "option -a not recognized"
    ##     print make_lens_atlas.__doc__  # will print the big comment above.
    ##     return


    ## for o,a in opts:
    ##     if o in ("-h", "--help"):
    ##         print make_lens_atlas.__doc__
    ##         return
    ##     elif o in ("--heatmap"):
    ##         flags['heatmap'] = True
    ##     elif o in ("--contour"):
    ##         flags['contour'] = True
    ##     elif o in ("--field"):
    ##         flags['field'] = True
    ##     elif o in ("--stamp"):
    ##         flags['stamp'] = True
    ##     elif o in ("--alpha"):
    ##         flags['alpha'] = True
    ##     elif o in ("--skill"):
    ##         flags['skill'] = True
    ##     elif o in ("--points"):
    ##         flags['points'] = int(a)
    ##     else:
    ##         assert False, "unhandled option"

    ## # Check for pickles in array args:
    ## if len(args) == 2:
    ##     #bureau_path = args[0]
    ##     collection_path = args[0]
    ##     catalog_path = args[1]
    ##     print "make_lens_atlas: illustrating behaviour captured in bureau, collection, and lens files: "
    ##     #print "make_lens_atlas: ", bureau_path
    ##     print "make_lens_atlas: ", collection_path
    ##     print "make_lens_atlas: ", catalog_path
    ## else:
    ##     print make_lens_atlas.__doc__
    ##     return

    # ------------------------------------------------------------------
    # Read in files:

    #bureau = swap.read_pickle(bureau_path, 'bureau')  # TODO: needed?
    collection = swap.read_pickle(collection_path, 'collection')
    catalog = csv2rec(catalog_path)

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
            ID = catalog[lens_i]['id']
            kind = catalog[lens_i]['kind']
            x = catalog[lens_i]['x']
            # flip y axis
            y = image_y_size - catalog[lens_i]['y']
            N0 = catalog[lens_i]['n0']
            if ((x < 0) * (y < 0)) + (N0 < flags['stamp_min']):
                # this is one of the 'non points'; skip
                continue
            subject = collection.member[ID]
            annotationhistory = subject.annotationhistory

            # ------------------------------------------------------------------
            # download png
            url = subject.location
            outname = flags['output_directory'] + '{0}_field.png'.format(ID)
            im = get_online_png(url, outname)
            min_x = np.int(np.max((x - flags['stamp_size'], 0)))
            max_x = np.int(np.min((x + flags['stamp_size'], im.shape[0])))
            min_y = np.int(np.max((y - flags['stamp_size'], 0)))
            max_y = np.int(np.min((y + flags['stamp_size'], im.shape[1])))

            min_member_x = np.int(np.max((x - flags['dist_max'], 0)))
            max_member_x = np.int(np.min((x + flags['dist_max'], im.shape[0])))
            min_member_y = np.int(np.max((y - flags['dist_max'], 0)))
            max_member_y = np.int(np.min((y + flags['dist_max'], im.shape[1])))
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

            fig = plt.figure(figsize=figsize_stamp)
            ax = fig.add_subplot(111)
            ax.imshow(im, origin=origin)

            ax.scatter(x - min_x,
                       y - min_y,
                       marker='d',
                       c=(0, 1.0, 0), s=100,
                       alpha=0.75)

            if ((flags['contour'])
                + (flags['heatmap'])
                + (flags['points'] != 0)):

                itwas = annotationhistory['ItWas']
                x_all = annotationhistory['At_X']
                y_all = annotationhistory['At_Y']

                x_markers_all = np.array([xi for xj in x_all for xi in xj])
                y_markers_all = np.array([yi for yj in y_all for yi in yj])

                # now filter markers by those that are within
                # dist_max of the center (since I don't record cluster
                # members...)
                agents_numbers = np.arange(
                        x_markers_all.size)
                conds = ((x_markers_all >= min_member_x) *
                         (x_markers_all <= max_member_x) *
                         (y_markers_all >= min_member_y) *
                         (y_markers_all <= max_member_y))
                agents = agents_numbers[conds]
                x_markers = x_markers_all[agents]
                y_markers = y_markers_all[agents]

                # filter markers
                n_catalog = len(agents)
                if (flags['points'] > 0) * \
                        (flags['points'] < n_catalog):
                    agents_points = np.random.choice(
                            agents,
                            size=flags['points'], replace=False)
                else:
                    agents_points = agents
                x_markers_filtered = x_markers_all[agents_points]
                y_markers_filtered = y_markers_all[agents_points]

                if (flags['skill']) * (len(agents) > 0):
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
                    skill = skill_all[agents]

                    smax = 100
                    smin = 5
                    if np.max(skill) != np.min(skill):
                        sizes_all = (skill_all - np.min(skill)) * (smax - smin) / \
                                (np.max(skill) - np.min(skill))
                        sizes_filtered = sizes_all[agents_points]
                    else:
                        sizes_filtered = 50
                    colors = [(0, 1.0, 0) for i in x_markers_filtered]
                else:
                    skill = None
                    sizes_filtered = 50
                    colors = (0, 1.0, 0)

                # ----------------------------------------------------------
                # heatmaps
                if (flags['heatmap']) * (len(agents) > 0):
                    fig_heatmap = plt.figure(figsize=figsize_stamp)
                    ax_heatmap = fig_heatmap.add_subplot(111)

                    # now do the lens locations
                    # don't need to filter the x's since that is filtered by
                    # xbins and ybins anyways
                    pdf2d(x_markers - min_x, y_markers - min_y,
                          xbins=xbins, ybins=ybins,
                          weights=skill, smooth=flags['smooth_click'],
                          color=(0, 1.0, 0),
                          style='hist',
                          axis=ax_heatmap)

                    if flags['alpha'] * (alpha != None):
                        contour_hist(alpha.T,
                            extent=(xbins[0], xbins[-1], ybins[0], ybins[-1]),
                            color='w', style='contour', axis=ax_heatmap)

                    ax_heatmap.tick_params(\
                        axis='both',          # changes apply to the x-axis
                        which='both',      # both major and minor ticks are affected
                        bottom='off',      # ticks along the bottom edge are off
                        top='off',         # ticks along the top edge are off
                        left='off',
                        right='off',
                        labelleft='off',
                        labelbottom='off') # labels along the bottom edge are off

                    # CPD 04.08.14: Flip axis to old conventions
                    ax_heatmap.invert_yaxis()
                    try:
                        outfile = flags['output_directory'] + \
                                    '{0}_cluster_{1}_heatmap.{2}'.format(
                                        ID, lens_i, flags['output_format'])
                        # fig_heatmap.savefig(outfile)
                        #fig_heatmap.canvas.print_png(outfile)
                        fig_heatmap.savefig(outfile, bbox_inches='tight', pad_inches=0)
                    except:
                        print 'make_lens_catalog: heatmap problem with ', ID, lens_i
                        # import ipdb; ipdb.set_trace()

                # ---------------------------------------------------------
                # back to our other plots
                # contours
                if (flags['contour']) * (len(agents) > 0):

                    # now do the lens locations
                    # don't need to filter the x's since that is filtered by
                    # xbins and ybins anyways
                    pdf2d(x_markers - min_x, y_markers - min_y,
                          xbins=xbins, ybins=ybins,
                          weights=skill, smooth=flags['smooth_click'],
                          color=(0, 1.0, 0),
                          style='contour',
                          axis=ax)

                # plot points
                if (flags['points'] != 0) * (len(agents) > 0):
                    ax.scatter(x_markers_filtered - min_x,
                               y_markers_filtered - min_y,
                               c=colors, s=sizes_filtered,
                               alpha=0.25)

            # plot alpha
            if flags['alpha'] * (alpha != None):
                contour_hist(alpha.T,
                    extent=(xbins[0], xbins[-1], ybins[0], ybins[-1]),
                    color='w', style='contour', axis=ax)

            # ----------------------------------------------------------
            ax.tick_params(\
                axis='both',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom='off',      # ticks along the bottom edge are off
                top='off',         # ticks along the top edge are off
                left='off',
                right='off',
                labelleft='off',
                labelbottom='off') # labels along the bottom edge are off

            ax.invert_yaxis()
            try:
                outfile = flags['output_directory'] + \
                            '{0}_cluster_{1}_contour.{2}'.format(
                                ID, lens_i, flags['output_format']
                                )
                # fig.savefig(outfile)
                fig.savefig(outfile, bbox_inches='tight', pad_inches=0)
                # fig.canvas.print_png(outfile)
            except:
                print 'make_lens_catalog: contour problem with ', ID, lens_i
                # import ipdb; ipdb.set_trace()
            plt.close('all')

    # ------------------------------------------------------------------
    # Fields
    if flags['field']:
        print "make_lens_atlas: running fields"
        # find the unique IDs. mark centers and also centrals if clustering is
        # done
        #import ipdb; ipdb.set_trace()
        unique_IDs = np.unique(catalog['id'])
        for ID in unique_IDs:
            mini_catalog = catalog[catalog['id'] == ID]
            subject = collection.member[ID]
            annotationhistory = subject.annotationhistory

            # plot cluster centers
            kind = mini_catalog['kind']
            x_centers = mini_catalog['x']
            # flip y from catalog
            y_centers = image_y_size - mini_catalog['y']
            skill_centers = mini_catalog['s']
            # filter out the -1 entry
            center_cond = (x_centers > 0) * (y_centers > 0)
            skill_centers = skill_centers[center_cond]
            x_centers = x_centers[center_cond]
            y_centers = y_centers[center_cond]
            colors_centers = [(0, 1.0, 0) for i in x_centers]

            if len(colors_centers) == 0:
                #welp, nothing here
                continue

            # ------------------------------------------------------------------
            # download png
            url = subject.location
            outname = flags['output_directory'] + '{0}_field.png'.format(ID)
            im = get_online_png(url, outname)

            # if it is a training image, claim the alpha parameter
            if im.shape[2] == 4:
                alpha = im[:, :, 3]
                im = im[:, :, :3]
            else:
                alpha = None

            fig = plt.figure(figsize=figsize_field)
            ax = fig.add_subplot(111)
            ax.imshow(im, origin=origin)
            xbins = np.arange(im.shape[0])
            ybins = np.arange(im.shape[1])
            min_x = 0
            min_y = 0
            max_x = im.shape[0]
            max_y = im.shape[1]

            if (flags['skill']) * (np.max(skill_centers) != np.min(skill_centers)):
                sizes_centers = (
                        (skill_centers - np.min(skill_centers)) *
                        (200 - 10) /
                        (np.max(skill_centers) - np.min(skill_centers)))
            else:
                sizes_centers = [100 for i in x_centers]
            ax.scatter(x_centers, y_centers,
                       marker='d', c=colors_centers,
                       s=sizes_centers, alpha=0.75)

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
            n_catalog = len(agents)
            if (flags['points'] > 0) * \
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
                skill = skill_all[agents]

                smax = 100
                smin = 5
                if np.max(skill) != np.min(skill):
                    sizes_all = (skill_all - np.min(skill)) * (smax - smin) / \
                            (np.max(skill) - np.min(skill))
                    sizes_filtered = sizes_all[agents_points]
                else:
                    sizes_filtered = 50
                colors = [(0, 1.0, 0) for i in x_markers_filtered]
            else:
                skill = None
                sizes_filtered = 50
                colors = (0, 1.0, 0)

            # ----------------------------------------------------------
            # contours
            if flags['contour'] * (len(x_markers) >= flags['stamp_min']):

                # now do the lens locations
                # don't need to filter the x's since that is filtered by
                # xbins and ybins anyways
                pdf2d(x_markers - min_x, y_markers - min_y,
                      xbins=xbins, ybins=ybins,
                      weights=skill, smooth=flags['smooth_click'],
                      color=(0, 1.0, 0),
                      style='contour',
                      axis=ax)

            # ----------------------------------------------------------
            # plot points
            if flags['points'] != 0:
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

            ax.invert_yaxis()
            try:
                outfile = flags['output_directory'] + '{0}_field_output.{1}'.format(ID, flags['output_format'])
                # fig.savefig(outfile)
                fig.savefig(outfile, bbox_inches='tight', pad_inches=0)
                #fig.canvas.print_png(outfile)
            except:
                print 'make_lens_catalog: field problem with field ', ID
            plt.close('all')

    print 'make_lens_catalog: All done!'

# ======================================================================

if __name__ == '__main__':
    # do argparse style; I find this /much/ easier than getopt (sorry Phil!)
    import argparse
    parser = argparse.ArgumentParser(description=make_lens_atlas.__doc__)
    # Options we can configure
    parser.add_argument("--output_directory",
                        action="store",
                        dest="output_directory",
                        default="./",
                        help="Output directory for images.")
    parser.add_argument("--output_format",
                        action="store",
                        dest="output_format",
                        default="png",
                        help="Format of output images.")
    parser.add_argument("--points",
                        action="store",
                        dest="points",
                        type=int,
                        default=30,
                        help="Number of points to plot. If < 0, do all points.")
    parser.add_argument("--image_y_size",
                        action="store",
                        dest="image_y_size",
                        type=int,
                        default=440,
                        help="Specify the y coordinate size of the image. Used for converting between database and catalog coordinate conventions.")
    # Actions we can specify
    parser.add_argument("--heatmap",
                        action="store_true",
                        dest="heatmap",
                        default=False,
                        help="Create heatmaps.")
    parser.add_argument("--contour",
                        action="store_true",
                        dest="contour",
                        default=False,
                        help="Create contour maps.")
    parser.add_argument("--alpha",
                        action="store_true",
                        dest="alpha",
                        default=False,
                        help="If true value is in the alpha coordinate, plot it.")
    parser.add_argument("--skill",
                        action="store_true",
                        dest="skill",
                        default=False,
                        help="Weight contours and heatmaps by skill.")
    parser.add_argument("--field",
                        action="store_true",
                        dest="field",
                        default=False,
                        help="Do atlas of whole field.")
    parser.add_argument("--stamp",
                        action="store_true",
                        dest="stamp",
                        default=False,
                        help="Do atlas of individual clusters.")
    # Required arguments
    parser.add_argument("collection",
                        help="Path to collection pickle.")
    parser.add_argument("catalog",
                        help="Path to catalog data file.")
    options = parser.parse_args()
    args = vars(options)

    import sys
    argv_str = ''
    for argvi in sys.argv:
        argv_str += argvi + ' '
    print(argv_str)
    make_lens_atlas(args)

# ======================================================================
