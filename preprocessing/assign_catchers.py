import os
import numpy as np
from skimage.external.tifffile import tifffile ## just latest version of tifffile
import argparse
from skimage.feature import peak_local_max
from scipy.signal import fftconvolve


parser = argparse.ArgumentParser(description = 'Identify catchers and write to \
                                 new file location')
parser.add_argument('-d', '--data_dir', required = True,
                    help = 'directory containing images with catchers to identify.')
parser.add_argument('-n', '--experiment_name', required = True,
                    help = 'name of files before channel, position and time.')
parser.add_argument('-t', '--top', required = True,
                    help = 'the top cutoff for the empty catcher to match to.')
parser.add_argument('-b', '--bottom', required = True,
                    help = 'the bottom cutoff for the empty catcher to match to.')
parser.add_argument('-l', '--left', required = True,
                    help = 'the left cutoff for the empty catcher to match to.')
parser.add_argument('-r', '--right', required = True,
                    help = 'the right cutoff for the empty catcher to match to.')
parser.add_argument('-p', '--position', required = True,
                    help = 'the position at timepoint 1 to find the empty catcher.')
args = parser.parse_args()
data_dir = args.data_dir
experiment_name = args.experiment_name
top = int(args.top)
bottom = int(args.bottom)
left = int(args.left)
right = int(args.right)
position = int(args.position)

def match_template_to_image(template, image, min_distance=25, threshold_rel=0.35):
    """ Uses fourier transforms to find peaks in image and locate catchers
    
        image -- 2d np array in which to look for catchers
        template -- 2d array with example of catcher -- cropped tight around catcher
        returns a list of array of coordinates where template occured in the image"""
    return peak_local_max(fftconvolve(image - np.mean(image),
                                      template[::-1, ::-1] -
                                      np.mean(template), 'same'),
                          min_distance=min_distance, 
                          threshold_rel=threshold_rel)
    
def find_catchers(timepoint,
                  pos,
                  name_format, # (pos, channel, time, filetype)
                  dest_parent_dir,
                  channel,
                  channel_number,
                  template,
                  experiment_directory):
    '''Finds catchers in image and writes to new file
    
        timepoint -- the timepoint to find catchers in
        pos -- the position to find catchers in
        name_format -- the name format to search for files
        dest_parent_dir -- directory to write out catcher locations
        experimental directory -- directory from which to pull data
        channel -- channel to search for catchers, default is BF
        channel_number -- channel number to search for catchers, default is 1'''
    tif_path = os.path.join(experiment_directory,
                            'Pos%d' % pos,
                             channel,
                             name_format % (pos, "c%d%s" % (channel_number, channel), timepoint))
    tif = tifffile.imread([tif_path])
    if len(tif.shape) > 2:
        tif = np.max(tif, axis=0)
    blobs = match_template_to_image(template,
                                    image=tif[0:512, 0:512],
                                    min_distance=100,
                                    threshold_rel=0.20)
    catcher_loc_path = os.path.join(
        dest_parent_dir,
        (name_format.split(".")[0]+".catcher_loc") %(pos, 
                                    "c%d%s" % (channel_number, channel), 
                                    timepoint))
    with open(catcher_loc_path, "w") as catcher_locs_fout:
        catcher_locs_fout.write('%s\t%s\n' % ('catcher_x_coord', 'catcher_y_coord'))
        for blob in blobs:
            catcher_locs_fout.write('%s\t%s\n' % (blob[1], blob[0]))
    return (tif, blobs)

def main():
    channel = 'BF'
    channel_number = 1
    t = 1
    name_format = experiment_name + '_Pos%d_%s_t%d.TIF'
    tif_path = os.path.join(data_dir,
                           'Pos%d' % position,
                            channel,
                            name_format % (position, "c%d%s" % (channel_number, channel), t))
    tif = tifffile.imread([tif_path])
    if len(tif.shape) > 2:
        tif = np.max(tif, axis = 0)
    cropped_reference_catcher = np.copy(tif[top:bottom,left:right])
    
    position_ref = os.listdir(data_dir)
    if '.DS_Store' in position_ref:
        position_ref.remove('.DS_Store')
    n_positions = len(position_ref)
    print('\n\n')
    try:
        os.mkdir(os.path.join(data_dir, 'catcher_locations'))
    except OSError:
        pass
    for pos in range(1,n_positions+1):
        try:
            tif, blobs = find_catchers(timepoint=1, pos=pos,
                           name_format=name_format, 
                           dest_parent_dir=os.path.join(data_dir, 'catcher_locations'),
                           channel=channel,
                           channel_number=channel_number,
                           template = cropped_reference_catcher,
                           experiment_directory=data_dir)
        except:
            raise

if __name__ == '__main__':
    main()


