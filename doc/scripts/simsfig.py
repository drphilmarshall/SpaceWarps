#!/usr/bin/env python
from PIL import Image
from pylab import *
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

##277,299 - lens center
fnamec="CFHTLS_028_2205_gri.png"
outputfile="output.pdf"
halfsize=50;

imgc = Image.open(fnamec)

def pltimg(imname,loca,xl,xh,yh,yl,descrip):
    ## Main image
    ax=subplot(3,3,loca);
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.text(0.5,0.1,descrip,transform=ax.transAxes,color="white",weight='bold',horizontalalignment='center',fontsize=8)
    ax.imshow(imname,cmap="YlOrBr_r");
    axins=zoomed_inset_axes(ax,2,loc=1)
    axins.imshow(imname,cmap="YlOrBr_r");
    
    ## Inset
    x1, x2, y1, y2 = xl,xh,yh,yl
    axins.set_xlim(x1, x2)
    axins.set_ylim(y1, y2)
    axins.xaxis.set_visible(False)
    axins.yaxis.set_visible(False)
    axins.spines['bottom'].set_color('white')
    axins.spines['top'].set_color('white')
    axins.spines['left'].set_color('white')
    axins.spines['right'].set_color('white')
    #mark_inset(ax,axins,loc1=2,loc2=4,fc="none",ec="white")

pltimg(imgc,1,277-halfsize,277+halfsize,299+halfsize,299-halfsize,"Group-Galaxy")

subplots_adjust(hspace=1e-1,wspace=0.05)
savefig(outputfile,bbox_inches="tight");
