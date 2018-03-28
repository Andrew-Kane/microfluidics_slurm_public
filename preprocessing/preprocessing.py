import os
import sys
import argparse
import re
import subprocess
import csv
import shutil

parser = argparse.ArgumentParser(description = 'Eliminate thumb images and \
                                 rename files by stage position labels.')
parser.add_argument('-d', '--directory', 
                    required = True, 
                    help = 'output directory from microscopy, containing  \
                    images and stage_positions.STG file')
parser.add_argument('-s', '--stage_ref',
                    required = False, default = 'none provided',
                    help = 'file for retrieving stage position number:name \
                    lookup. defaults to stage_positions.STG or \
                    stage_positions.txt')
args = parser.parse_args()
directory = args.directory
s = args.stage_ref

def main():
    os.chdir(directory)
    subprocess.call("rm *thumb*", shell =
                True) # rm thumbs
    # Finds stage position file and assigns the file to stage_ref variable
    if s != 'none provided':
        stage_ref = s 
    elif 'stage_positions.STG' in os.listdir():
        stage_ref = 'stage_positions.STG'
    elif 'stage_positions.txt' in os.listdir():
        stage_ref = 'stage_positions.txt'
    else:
        sys.exit('No stage position reference file provided.')
    #For confirmation, prints stage reference file identified and the directory in which it is located
    print('stage reference file: ' + stage_ref)
    print('current working directory: ' + os.getcwd())
    #Creates a list of all the stage positions in the stage reference file.
    spos_f = open(stage_ref,'r')
    spos_reader = csv.reader(spos_f)
    stage_pos = []
    line = 0
    for row in spos_reader:
        if line < 4:
            pass
        else:
            print('current line:')
            print(row)
            stage_pos.append(row[0])
        line = line + 1
    print('stage position name list:')
    print(stage_pos)
    #Identifies all .tif files and stores them in img_files variable.
    img_files = [f for f in os.listdir() if '.tif' in f.lower()]
    img_files = tuple(img_files)
    #For confirmation, prints list of stages
    print('list of image files:')
    print(img_files)
    # Creates data file directory for further processing.
    try:
        os.mkdir(os.path.join(directory,'src_img'))
    except FileExistsError:
        pass
    new_directory = os.path.join(directory,'src_img')
    #Creates subdirectories within each experimental file for each stage position
    for x in range(0,len(stage_pos)):
        val = x+1
        try:
            os.mkdir(os.path.join(new_directory,'Pos%d'%val))
        except FileExistsError:
            pass
    #Checks what channels have been used and assigns them to the channels variable
    # Note: names of experiments in save must be two words long, ex "Date_Exp#"
    check_channels = []
    for x in range(0,len(img_files)):
        check_channels.append(img_files[x].split('_'))
    if len(check_channels[0]) >= 5:
        channels = []
        for x in range(0,len(check_channels)):
            if check_channels[x][2][2:] in channels:
                pass
            else:
                channels.append(check_channels[x][2][2:])
    else:
        channels = ['BF']
    #Uses values of channels to make directories within each position folder
    #If a single channel is used, it is assumed this is brightfield and makes an appropriate directory       
    for channel in range(0,len(channels)):
        for x in range(0,len(stage_pos)):
            val = x+1
            try:
                os.mkdir(os.path.join(new_directory,'Pos%d'%val,channels[channel]))
            except FileExistsError:
                pass
    
    if len(channels) > 1:
        for x in range(0,len(channels)):
            #If a single channel is used, it is assumed this is brightfield and makes an appropriate directory
            channel_files = [f for f in os.listdir() if channels[x].lower() in f.lower()] 
            channel_num = str(x+1)
            if channel_files != []:
                #Creates list with files renamed by replacing w in channel with c followed by channel number, starting with 1
                renamed_channel_files = ['']*len(channel_files)
                for x in range(0,len(renamed_channel_files)):
                    renamed_channel_files[x] = re.sub('w\d+',
                                                 'c'+ channel_num,
                                                 channel_files[x])
                #Rearranges channel name so that channel and position are swapped.
                rearranged_channel_files = []
                for x in range(0,len(renamed_channel_files)):
                    rearranger = renamed_channel_files[x].split('_')
                    rearranged = list(rearranger)
                    rearranged[2] = rearranger[3]
                    rearranged[3] = rearranger[2]
                    rearranged_channel_files.append('_'.join(rearranged))
                # Renames files to replace 's' for stage with 'Pos' for proper naming
                stage_re = re.compile('s\d+')
                stage_IDs = []
                for x in range(0,len(rearranged_channel_files)):
                    stage_IDs.append(int(stage_re.search(rearranged_channel_files[x]).group()[1:]))
                renamed_pos_files = ['']*len(rearranged_channel_files)
                for x in range(0,len(rearranged_channel_files)):
                    renamed_pos_files[x] = re.sub('s\d+',
                                              'Pos%d'%stage_IDs[x],
                                                rearranged_channel_files[x])
                rename_dict = dict(zip(channel_files, renamed_pos_files))
                for key in rename_dict:
                    # rename files
                    os.rename(key,rename_dict[key].replace(' ',' '))
    # Renames if no specified channel.
    else:
        stage_re = re.compile('s\d+')
        stage_IDs = []
        for x in range(0,len(img_files)):
            stage_IDs.append(int(stage_re.search(img_files[x]).group()[1:]))
        renamed_img_files = ['']*len(img_files)
        for x in range(0,len(renamed_img_files)):
            renamed_img_files[x] = re.sub('s\d+',
                                          'Pos%d'%stage_IDs[x]+'_c1BF',
                                            img_files[x])
        rename_dict = dict(zip(img_files, renamed_img_files))
        for key in rename_dict:
        # rename files
            os.rename(key,rename_dict[key].replace(' ',' '))
    #Moves files to their appropriate directories
    new_img_files = [f for f in os.listdir() if '.tif' in f.lower()]
    stage_assign = re.compile('Pos\d+')
    for x in range(0,len(new_img_files)):
        try:
            shutil.move(os.path.join(directory,
                                     new_img_files[x]),
                    os.path.join(new_directory,
                                 stage_assign.search(new_img_files[x]).group()[0:],
                                                    new_img_files[x]))
        except FileExistsError:
            pass
    for x in range(0,len(stage_pos)):
        val = x+1
        os.chdir(os.path.join(new_directory,
        'Pos%d'%val))
        new_img_files = [f for f in os.listdir() if '.tif' in f.lower()]
        channel_assign = re.compile('c\d+')
        for x in range (0,len(new_img_files)):
            try:
                shutil.move(os.path.join(new_directory,
                                       'Pos%d'%val,
                                        new_img_files[x]),
                           os.path.join(new_directory,
                                       'Pos%d'%val,
                                       channels[int(channel_assign.search(new_img_files[x]).group()[1:])-1],
                                        new_img_files[x]))
            except FileExistsError:
                pass

if __name__ == '__main__':
    main()

