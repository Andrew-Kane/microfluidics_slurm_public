import os
import shutil
import argparse

parser = argparse.ArgumentParser(description = 'Reassign images into subfolder \
                                 to allow segmentation.')
parser.add_argument('-d', '--img_dir', required = True, 
                    help = 'directory containing images to segment.')

args = parser.parse_args()
direc_name = args.img_dir

files = os.listdir(direc_name)
folders = [i for i in files if 'stage_' in i.lower()]
folders.remove('stage_positions.STG')

for folder in range(len(folders)):
    imgs =[]
    os.chdir(os.path.join(direc_name,folders[folder]))
    imgs = [f for f in os.listdir() if 'tif' in f.lower()]
    for img in imgs:
        shutil.move(os.path.join(direc_name,folders[folder],img),direc_name)
        
for folder in range(len(folders)):
    shutil.rmtree(os.path.join(direc_name,folders[folder]))