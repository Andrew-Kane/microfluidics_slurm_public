import os
import random ## use to get a random positions for spot checking
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors 
from skimage.external.tifffile import tifffile ## just latest version of tifffile
from skimage import filters
## For progress bar
import ipwidgets
from ipywidgets import FloatProgress
from IPython.display import display
import argparse
from catcher_finder import match_template_to_image
from catcher_finder import find_catchers


parser = argparse.ArgumentParser(description = 'Identify catchers and write to \
                                 new file location')
parser.add_argument('-d', '--data_dir', required = True,
                    help = 'directory containing images with catchers to identify.')
parser.add_argument('-n', '--experiment_name', required = True,
                    help = 'name of files before channel, position and time.')
parser.add_argument('-t', 'top', required = True,
                    help = 'the top cutoff for the empty catcher to match to.')
parser.add_argument('-b', 'bottom', required = True,
                    help = 'the bottom cutoff for the empty catcher to match to.')
parser.add_argument('-l', 'left', required = True,
                    help = 'the left cutoff for the empty catcher to match to.')
parser.add_argument('-r', 'right', required = True,
                    help = 'the right cutoff for the empty catcher to match to.')
parser.add_argument('-p', 'position', required = True,
                    help = 'the position at timepoint 1 to find the empty catcher.')
args = parser.pars_args()
data_dir = args.data_dir
experiment_name = args.experiment_name
top = args.top
bottom = args.bottom
left = args.left
right = args.right
position = args.position

def main():
    channel = 'BF'
    channel_number = 1
    t = 1
    name_format = experiment_name + '_Pos%d_%s_t%d.tif'
    tif_path = os.path.join(data_dir,
                           'Pos%d' % position,
                            channel,
                            name_format % (position, "c%d%s" % (channel_number, channel), t))
    tif = tifffile.imread([tif_path])
    if len(tif.shape) > 2:
        tif = np.max(tif, axis = 0)
    cropped_reference_catcher = np.copy(tif[top:bottom,left:right])
    
    position_ref = os.listdir(data_dir)
    if '.DS_Store' in postion_ref:
        position_ref.remove('.DS_Store')
    n_positions = len(position_ref)
    f = FloatProgress(min=0, max=n_positions, description="Finding catchers...")
    display(f)
    print('\n\n')
    try:
        os.mkdir(os.path.join(data_dir, 'catcher_locations'))
    except OSError:
        pass
    for pos in range(1,n_positions+1):
        val = pos-1
        f.description = "Finding catchers...Pos%d" % pos
        f.value += 1
        try:
            tif, blobs = find_catchers(timepoint=1, pos=pos,
                           name_format=name_format, 
                           dest_parent_dir=os.path.join(data_dir, 'catcher_locations'),
                           experiment_directory=data_dir)
        except:
            raise



