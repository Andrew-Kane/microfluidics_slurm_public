import os
import sys
import argparse
import re
import subprocess
import csv
import copy
from skimage.external.tifffile import tifffile

parser = argparse.ArgumentParser(description = 'Eliminate thumb images and \
                                 rename files by stage position labels.')
parser.add_argument('-d', '--directory', 
                    required = True, 
                    help = 'output directory from microscopy, containing  \
                    images and stage_positions.STG file')
parser.add_argument('-n', '--experiment_name', required = True,
                    help = 'name of files before channel, position and time.')
args = parser.parse_args()
directory = args.directory
experiment = args.experiment_name

def main():
    os.chdir(directory)
    #Identifies all .tif files and stores them in img_files variable.
    img_files = [f for f in os.listdir() if '.tif' in f.lower()]
    img_files.sort()
    img_files = tuple(img_files)
    #For confirmation, prints list of stages
    print('list of image files:')
    print(img_files)
    #Breaks tif video files into multiple tifs for each timepoint and renames them
    for i in range(len(img_files)):
        print('Processing position image '+img_files[i])
        tiff = tifffile.imread(img_files[i])
        pos= i+1
        for j in range(len(tiff)):
            time = j+1
            tifffile.imsave(filename=directory+experiment+'_s%d'%pos+'_t%d.TIF'%time,
                                        data=tiff[j])
        os.remove(img_files[i])

if __name__ == '__main__':
    main()

