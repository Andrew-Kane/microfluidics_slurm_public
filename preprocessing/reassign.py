import os
import shutil

import argparse

parser = argparse.ArgumentParser(description = 'Reassign images into subfolder \
                                 to allow segmentation.')
parser.add_argument('-d', '--img_dir', required = True, 
                    help = 'directory containing images to segment.')

args = parser.parse_args()
direc_name = args.img_dir

channel_name = 'bf'

files = os.listdir(direc_name)
imgfiles = [i for i in files if channel_name in i.lower()]
segmentfiles = [f for f in imgfiles if 'thumb' not in f.lower()]
segmentfiles.sort()

folders = []
for im in range(len(segmentfiles)):
    foldername = int(segmentfiles[im].split('_')[3][1:])
    if foldername in folders:
        pass
    else:
        folders.append(foldername)

for folder in range(len(folders)):
    try:
        os.mkdir(os.path.join(direc_name,'stage_'+str(folders[folder])))
    except FileExistsError:
        pass
    
for img in range(len(segmentfiles)):
     shutil.move(os.path.join(direc_name,segmentfiles[img]),
                       os.path.join(direc_name,'stage_'+segmentfiles[img].split('_')[3][1:]))