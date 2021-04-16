import os
import sys
sys.path.append('/n/home06/akane/code/')
import argparse
from microfluidics import Segment
import numpy as np
import pandas as pd
from skimage import io
import pickle
import re
import json

parser = argparse.ArgumentParser(description = 'Measure fluorescence \
                                 intensity and other properties \
                                 in mother cells.')
parser.add_argument('-d', '--img_dir', required = True, 
                    help = 'directory containing images to segment.')
parser.add_argument('-e', '--experiment_name', required = True,
                    help = 'name of the experiment.')
parser.add_argument('-n', '--array_number', required = True,
                    help = 'the job number within the job array.')
parser.add_argument('-a', '--array_length', required = True,
                    help = 'length of the job array.')


args = parser.parse_args()
print(args)
img_dir = args.img_dir
experiment_name = args.experiment_name
array_n = int(args.array_number)
array_l = int(args.array_length)

def main():
  '''Creates a dataframe for lifepsans by taking annotaed json file 
  containing yeast budding events, masks generated from DeepCell 
  segmentation and cleanup, and fluorescence images. Dataframe contains
  information for each frame about the age of the yeast, the mother
  cell's fluorescence intensity, volume, age, and final lifespan.'''
    #Open annotation file for budding events and cell deaths.
    json_file = os.path.join(img_dir,str(experiment_name)+'.json')
    with open(json_file, 'r') as tmp:
        annotations = json.load(tmp)

    #Creates lifespans dataframe for total lifespans of lineages.
    lifespans = pd.DataFrame(columns=['filename', 'buds_counted', 'is_death'], index=['filename'])
    lifespans = lifespans.dropna()
    for filename, annotation in annotations.items():
        if annotation['budding_events'] is None:
            continue
        for cell in get_lifespan_from_annotation(annotation['budding_events']):
            buds_counted, is_death = cell
            lifespans.loc[filename]=[filename, buds_counted, is_death]

    #Get fluorescent images.
    os.chdir(img_dir)
    files = [f for f in os.listdir() if '.tif' in f.lower()]
    gfp_imgs = [y for y in files if 'gfp' in y.lower()]

    #Intialize output dataframe.
    output_frame = pd.DataFrame({'img': [],
                                     'frame_num': [],
                                     'obj_channel': [],
                                     'obj_number': [],
                                     'volume': [],
                                     'gfp_mean': [],
                                     'gfp_stdev': [],
                                     'lifespan': [],
                                     'age':[],
                                     'cell_cycle':[],
                                     'budding':[]
                                    })

    #Obtain pickles and fluorescence images that they correspond to.
    pickles = get_pickle_set(img_dir, array_l, array_n)
    print(pickles)
    os.chdir(img_dir + '/pickles')
    os.listdir()
    pickle_list = [p for p in os.listdir() if '.pickle' in p]
    gfp_ids = get_img_ids(gfp_imgs)
    gfp_ids = {v: k for k, v in gfp_ids.items()}

    for p in pickles:
      #Opens pickle files for applying segmentation to fluorescence images.
        os.chdir(img_dir + '/pickles')
        cfile = open(p,'rb')
        cpickle = pickle.load(cfile)
        print('current segmented object image: ' + cpickle.filename)
        (pickle_id, pickle_channel) = get_img_ids([cpickle.filename],
                                                  return_channel = True)
        pickle_id = pickle_id[cpickle.filename]
        pickle_channel = pickle_channel[cpickle.filename]
        print('current segmented object identifier: ' + pickle_id)
        print('current segmented object channel: ' + pickle_channel)
        os.chdir(img_dir)
        print('current GFP image file: ' + gfp_ids[pickle_id])
        gfp_img = io.imread(gfp_ids[pickle_id])
        annotation_id = pickle_id.capitalize() + '_BF.tif'
        print(annotation_id)
        gfp_mean = {}
        volumes_v2 = {}
        gfp_stdev = {}
        cell_cycle = 0
        age = 0
        new_lifespan = 'no'
        #Goes through each frame in a lifespan and determines GFP intensity and volume of the mother cell.
        for frame in range(len(cpickle.mother_nums)):
            print(frame)
            gfp_mean = {}
            volumes_v2 = {}
            gfp_stdev = {}
<<<<<<< HEAD
            print(lifespans['buds_counted'][lifespans['filename'] == annotation_id])
            lifespan = int(lifespans['buds_counted'][lifespans['filename'] == annotation_id])
            if annotations[annotation_id]['budding_events'][frame] == 'n':
                new_lifespan = 'yes'
                cell_cycle = 0
                age = 0
            elif annotations[annotation_id]['budding_events'][frame] == 'b':
                if new_lifespan == 'yes':
                    cell_cycle = 0
                    age += 1
            elif annotations[annotation_id]['budding_events'][frame] == 'x':
                break
            else:
                if new_lifespan == 'yes':
                    cell_cycle += 1
            if new_lifespan == 'no':
=======
            #Ignores frames with no cells present
            if len(cpickle.mother_nums[frame]) == 0:
>>>>>>> b6fe5cc41337b8e3fdb3d8eab43cac4a14435d37
                pass
            else:
                print('     current frame number: ' + str(frame))
                for obj in cpickle.mother_nums[frame]:
                            print('     current obj number: ' + str(obj))
                            frame_num = frame
                            gfp_mean[obj] = np.mean(gfp_img[frame][cpickle.mother_cells[frame] == obj])
                            volumes_v2[obj] = len(np.flatnonzero(cpickle.mother_cells[frame] == obj))
                            gfp_stdev[obj] = np.std(gfp_img[frame_num][cpickle.mother_cells[frame] == obj])
<<<<<<< HEAD
=======
                lifespan = int(lifespans['buds_counted'][lifespans['filename'] == annotation_id])
                #n indicates new lifespan in the json annotated file
                if annotations[annotation_id]['budding_events'][frame] == 'n':
                    new_lifespan = 'yes'
                    cell_cycle = 0
                    age = 0
                elif annotations[annotation_id]['budding_events'][frame] == 'b':
                    if new_lifespan == 'yes':
                        cell_cycle = 0
                    age += 1
                elif annotations[annotation_id]['budding_events'][frame] == 'x':
                    break
                else:
                    if new_lifespan == 'yes':
                        cell_cycle += 1
>>>>>>> b6fe5cc41337b8e3fdb3d8eab43cac4a14435d37
                currframe_data = pd.DataFrame({'img': pd.Series(data =
                                                              [cpickle.filename]*len(cpickle.mother_nums[frame]),
                                                              index = cpickle.mother_nums[frame]),
                                             'obj_channel': pd.Series(data =
                                                                      [pickle_channel]*len(cpickle.mother_nums[frame]),
                                                                  index = cpickle.mother_nums[frame]),
                                             'obj_number': pd.Series(data = cpickle.mother_nums[frame],
                                                                     index = cpickle.mother_nums[frame]),
                                             'volume': volumes_v2,
                                             'gfp_mean': gfp_mean,
                                             'gfp_stdev': gfp_stdev,
                                             'frame_num':frame_num,
                                               'lifespan': lifespan,
                                               'age': age,
                                               'cell_cycle':cell_cycle,
                                               'budding':annotations[annotation_id]['budding_events'][frame]
                                            })
                output_frame = pd.concat([output_frame, currframe_data])
    print('')
    print('-----------------------------------------------------------------')
    print('-----------------------------------------------------------------')
    print('')
    print('saving data...')
    if not os.path.isdir(img_dir + '/analysis_output'):
        os.mkdir(img_dir + '/analysis_output')
    output_frame.to_csv(img_dir + '/analysis_output/' + str(array_n) +
                        '_analysis_output.csv')

def get_pickle_set(img_dir, array_l, array_n):
    '''Get the subset of pickles for analysis by a given instance.'''
    os.chdir(img_dir + '/pickles')
    pickle_list = [p for p in os.listdir() if '.pickle' in p]
    pickle_list.sort()
    pickles_per_job = int(len(pickle_list)/array_l)
    split_pickle_list = []
    for i in range(0, len(pickle_list), pickles_per_job):
        split_pickle_list.append(pickle_list[i:i+pickles_per_job])
    n_leftover = len(pickle_list)%array_l
    if n_leftover != 0:
        leftover_pickles = pickle_list[-n_leftover:]
        for x in range(0,len(leftover_pickles)):
            split_pickle_list[x].append(leftover_pickles[x])
    return(split_pickle_list[array_n])

def get_img_ids(img_files, return_channel = False):
    '''Extracts image filenames lacking wavelength identifiers.'''
    img_ids = []
    channels = []
    for img in img_files:
        print('_______________________________________________________')
        print('     generating image identifier for ' + img)
        split_im = img.split('_')
        rm_channel = '_'.join(split_im[:3]).lower()
        channel = split_im[3]
        channel = channel.split('.')[0]
        print('     image identifier: ' + rm_channel)
        print('     channel: ' + channel)
        img_ids.append(rm_channel)
        channels.append(channel)
    fname_id_dict = dict(zip(img_files, img_ids))
    channel_dict = dict(zip(img_files, channels))
    print('')
    print('done extracting image identifiers.')
    if not return_channel:
        return(fname_id_dict)
    if return_channel:
        return((fname_id_dict, channel_dict))
    
def get_lifespan_from_annotation(annotation_string):
  '''Gets lifespan from json annoatation file. '''
        lifespans = "".join([i for i in annotation_string if i in ['n','b', 'w', 'x']]).split("n")
        for i in lifespans:
            i.rstrip('b')
        return [(i.count('b'), i.endswith('x')) for i in lifespans if 'b' in i]
    
if __name__ == '__main__':
    main()
