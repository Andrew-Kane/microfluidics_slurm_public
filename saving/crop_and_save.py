import sys
sys.path.append('/n/home06/akane/code/')
from tools import stack_registration
import os
import numpy as np
from skimage.external.tifffile import tifffile
import argparse

parser = argparse.ArgumentParser(description = 'Identify catchers and write to \
                                 new file location')
parser.add_argument('-d', '--data_dir', required = True,
                    help = 'directory containing images with catchers to identify.')
parser.add_argument('-n', '--experiment_name', required = True,
                    help = 'name of files before channel, position and time.')
parser.add_argument('-p', '--projection_type', required = True,
                    help = 'whether to project for combining images.')
parser.add_argument('-c', '--combine', required = True,
                    help = 'whether to combine different channels into one tif.')
parser.add_argument('-a', '--array_number', required = True,
                    help = 'the job number within the job array.')
parser.add_argument('-l', '--array_length', required = True,
                    help = 'length of the job array.')


args = parser.parse_args()
data_dir = args.data_dir
experiment_name = args.experiment_name
projection_type = args.projection_type
combine = args.combine
array_n = int(args.array_number)
array_l = int(args.array_length)

def main():
    # Primes the script for what channel to do stack registration on.
    name_format = experiment_name + '_Pos%d_c%d%s_t%d.%s'
    os.chdir(data_dir)
    # For different data storage types
    if 'src_img' in os.listdir(data_dir):
        img_dir = os.path.join(data_dir, 'src_img')
    else:
        img_dir = data_dir
    processed_dir = os.path.join(data_dir, 'processed_images')
    catcher_dir = os.path.join(img_dir, 'catcher_locations')
    drift_dir = os.path.join(data_dir, 'drift_corrections')
    try:
        os.mkdir(processed_dir)
    except FileExistsError:
        pass
    try:
        os.mkdir(drift_dir)
    except FileExistsError:
        pass
    # Determines which positions to align and crop in this node.
    if 'src_img'in os.listdir(data_dir):
        os.chdir(os.path.join(img_dir))
        positions = os.listdir(os.path.join(img_dir))
    else:
        positions = os.listdir(img_dir)
    if '.DS_Store' in positions:
        positions.remove('.DS_Store')
    if '._.DS_Store' in positions:
        positions.remove('._.DS_Store')
    if 'stage_positions.STG' in positions:
        positions.remove('stage_positions.STG')
    if 'catcher_locations' in positions:
        positions.remove('catcher_locations')
    if 'processed_images' in positions:
        positions.remove('processed_images')
    if 'drift_corrections' in positions:
        positions.remove('drift_corrections')
    positions.sort()
    positions_per_job = int(len(positions)/array_l)
    split_positions_list = []
    for i in range(0, len(positions), positions_per_job):
        split_positions_list.append(positions[i:i+positions_per_job])
    n_leftover = len(positions)%array_l
    if n_leftover != 0:
        leftover_positions = positions[-n_leftover:]
        for x in range(0,len(leftover_positions)):
            split_positions_list[x].append(leftover_positions[x])
    positions_list = split_positions_list[array_n]
    print('Positions:')
    print(positions_list)
    # Cycles over every position in the node and aligns and crops.
    for i in range(0,len(positions_list)):
        os.chdir(img_dir)
        channel = 'BF'
        channel_number = 1
        print('Aligning and cropping ' + positions_list[i])
        pos = int(positions_list[i][3:])
        num_timepoints = len(os.listdir(os.path.join(img_dir,
                                                     'Pos%d' % pos, 
                                                     channel)))
        timepoints = num_timepoints
        crop_window_h = 250
        crop_window_w = 250
        timestep = 1

        catcher_found_at_t = 1
        
        # open one tiff to find shape
        tif_path = os.path.join(img_dir,
                                'Pos%d' % pos,
                                channel,
                                name_format % (pos, channel_number, channel, 1, "TIF"))
        tif = tifffile.imread([tif_path])
        default_shape = tif.shape
        #check shape to see if it is compatible
        if len(default_shape)==2:
            to_align = np.zeros((timepoints//timestep, 1, 1,default_shape[-2], default_shape[-1]), dtype='uint16') ## create an empty array to hold all of the images
        elif len(default_shape)==3:
            if projection_type == 'None':
                to_align = np.zeros((timepoints//timestep, default_shape[0], 1, default_shape[-2], default_shape[-1]), dtype='uint16') ## create an empty array to hold all of the images
            else:
                to_align = np.zeros((timepoints//timestep, 1, 1,default_shape[-2], default_shape[-1]), dtype='uint16') ## create an empty array to hold all of the images
        else:
            raise ValueError('The tif is not in a shape that we expected')
        
        for t in range(0, timepoints, timestep):
            tif_path = os.path.join(img_dir,
                                    'Pos%d' % pos,
                                    channel,
                                    name_format % (pos, channel_number, channel, t+1, "TIF"))
            try:
                tif = tifffile.imread([tif_path])
                if projection_type == 'max':
                    tif = np.max(tif, axis=0)
                    tif = np.expand_dims(tif, axis=0)
                elif projection_type == 'sum':
                    tif = np.sum(tif, axis=0)
                    tif = np.expand_dims(tif, axis=0)
                elif projection_type == 'None':
                    pass
            except ValueError:
                tif = np.zeros(default_shape)
                print("Unable to read: ", name_format % (pos, channel_number, channel, t, "TIF"))
            try:
                to_align[t//timestep, :, 0, :, :] = tif[0:default_shape[-2], 0:default_shape[-1]]
            except IndexError:
                pass
        print("Aligning...", end = "")
        reg_h = default_shape[-2]//2
        reg_w = default_shape[-1]//2
        reg_x = default_shape[-1]//2
        reg_y = default_shape[-2]//2
        # Corrects for drift changes using stack registration.
        drift_corrections = stack_registration.stack_registration(s=to_align[:,
                                to_align.shape[1]//2,
                                 0,
                                reg_y-reg_h//2:reg_y+reg_h//2,
                                reg_x-reg_w//2:reg_x+reg_w//2],
                                align_to_this_slice=0,
                                refinement='spike_interpolation',
                                register_in_place=False,
                                fourier_cutoff_radius=None,
                                debug = False)
        drift_corrections_path = os.path.join(drift_dir,
                                      name_format % (
                                          pos, 
                                          1, 
                                          'BF', 
                                          catcher_found_at_t, 
                                          "drift"))
        # writes drift corrections
        with open(drift_corrections_path, "w") as drift_corrections_fin:
            drift_corrections_fin.write('\\t'.join(['t', 'y-drift', 'x-drift'])+'\\n')
            for t, drift in enumerate(drift_corrections):
                drift_corrections_fin.write('\\t'.join(['%d' % (t+1), '%d' % drift[0], '%d' % drift[1]])+'\\n')
        # Checks if there are other channels in this experiment
        channels = os.listdir(os.path.join(img_dir, "Pos%d" % pos))
        if '.DS_Store' in channels:
            channels.remove('.DS_Store')
        if '._.DS_Store' in channels:
            channels.remove('._.DS_Store')
        os.listdir(os.path.join(img_dir, "Pos%d" % pos))
        channels = sorted(channels)
        channels.pop(channels.index("BF"))
        channels_to_omit = []
        fluoro_images = []
        # Imports fluorescence channels to assemble in hyperstack with BF images.
        for channel in channels:
            if channel in channels_to_omit:
                continue
           # if len(os.listdir(os.path.join(img_dir, "Pos%d" % pos, channel))) < 10:
            #    continue
            for i in range(100):
                try:
                    channel_number = int(os.listdir(os.path.join(img_dir, "Pos%d" % pos, channel))[0].split("_")[3][1])
                    break
                except:
                    pass
            images = np.zeros((timepoints//timestep, 1, 1, default_shape[-2], default_shape[-1]), dtype='uint16')
            for t in range(0, timepoints, timestep):
                tif_path = os.path.join(img_dir, 'Pos%d' % pos, channel, name_format % (pos, channel_number, channel, t+1, "TIF"))
                try:
                    tif = tifffile.imread([tif_path])
                    if len(tif.shape)==2:
                        tif = np.expand_dims(tif, axis=0)
                    if projection_type == 'max':
                        tif = np.max(tif, axis=0)
                        tif = np.expand_dims(tif, axis=0)
                    elif projection_type == 'sum':
                        tif = np.sum(tif, axis=0)
                        tif = np.expand_dims(tif, axis=0)
                    elif projection_type == 'None':
                        pass
                    if tif.shape[0] > images.shape[1]:
                        to_pad = np.zeros((timepoints//timestep,
                                           tif.shape[0]-images.shape[1],
                                            1,
                                            default_shape[-2], 
                                            default_shape[-1]), dtype='uint16')
                        images = np.concatenate((images, to_pad), axis=1)
                except ValueError:
                    tif = np.zeros(tif.shape)
                    print("Unable to read: ", name_format % (pos, channel_number, channel, t, "tif"))
                try:
                    images[t//timestep, :, 0, :,:] = tif[:, :, :]
                except IndexError:
                    raise 
        
            fluoro_images.append(images)
        ## Assemble hyperstack
        total_stack = np.zeros((timepoints//timestep, #t
                                    1, #z
                                    len(fluoro_images)+1, #c
                                    to_align.shape[-2], #y
                                    to_align.shape[-1]), dtype=to_align.dtype)
        for i in range(-1, len(fluoro_images)):
            if i==-1:
                images = to_align
            else:
                images = fluoro_images[i]
            if images.shape[1] > total_stack.shape[1]:
                to_pad = np.zeros((timepoints//timestep,
                                   images.shape[1]-total_stack.shape[1],
                                    total_stack.shape[2],
                                    default_shape[-2], 
                                    default_shape[-1]), 
                                    dtype=total_stack.dtype)
                total_stack = np.concatenate((total_stack, to_pad), axis=1)
            total_stack[:, :, i+1, :, :] = images[:, :, 0, :, :]
        ## Apply drift corrections to hyperstack
        print("Done")
        print("Applying alignment...", end = "")
    
        for c in range(total_stack.shape[2]):
            for z in range(total_stack.shape[1]):
                stack_registration.apply_registration_shifts(total_stack[:, z, c, :, :], drift_corrections)
        
        ## Load in catcher locations
        catcher_loc_path = os.path.join(
                catcher_dir,
                name_format % (pos, 1, 'BF', 1, "catcher_loc"))
        catchers = []
        with open(catcher_loc_path, "r") as catcher_locs_fin:
            header = catcher_locs_fin.readline()
            for line in catcher_locs_fin:
                catcher_x, catcher_y = line.strip().split('	')
                catchers.append((catcher_x, catcher_y))
        print("Done")
        
        ## For catcher in catchers, crop, and saveout tif
        if combine == 'combine':
            for catcher in catchers:
                try:
                    catcher_x, catcher_y = [round(float(i)) for i in catcher]
                    cropped_image_name = "Pos%d_x%d_y%d.tif" % (pos, catcher_x, catcher_y)
                    out_path = os.path.join(processed_dir, cropped_image_name)
                    try:
                        to_save = total_stack[:, :, :, 
                                                  catcher_y-crop_window_h//2:catcher_y+crop_window_h//2,
                                                  catcher_x-crop_window_w//2:catcher_x+crop_window_w//2]
                    except: 
                        to_save = total_stack[:, :, :, 
                                                  catcher_y-crop_window_h//2:catcher_y+crop_window_h//2-28,
                                                  catcher_x-crop_window_w//2:catcher_x+crop_window_w//2-28]
    
                    tifffile.imsave(filename=out_path,
                                    data=np.squeeze(to_save))
                except:
                    pass
        elif combine == 'separate':
            for catcher in catchers:
                try:
                    catcher_x, catcher_y = [round(float(i)) for i in catcher]
                    cropped_image_name = "Pos%d_x%d_y%d_BF.tif" % (pos, catcher_x, catcher_y)
                    out_path = os.path.join(processed_dir, cropped_image_name)
                    try:
                        to_save = total_stack[:, 0, 0, 
                                                  catcher_y-crop_window_h//2:catcher_y+crop_window_h//2,
                                                  catcher_x-crop_window_w//2:catcher_x+crop_window_w//2]
                    except: 
                        to_save = total_stack[:, 0, 0, 
                                                  catcher_y-crop_window_h//2:catcher_y+crop_window_h//2-28,
                                                  catcher_x-crop_window_w//2:catcher_x+crop_window_w//2-28]

                    tifffile.imsave(filename=out_path,
                                    data=np.squeeze(to_save))
                except:
                    pass
            for channel in channels:
                for i in range(100):
                    try:
                        channel_number = int(os.listdir(os.path.join(data_dir, "Pos%d" % pos, channel))[0].split("_")[3][1])
                        break
                    except:
                        pass
                for catcher in catchers:
                    try:
                        catcher_x, catcher_y = [round(float(i)) for i in catcher]
                        cropped_image_name = "Pos%d_x%d_y%d_%s.tif" % (pos, catcher_x, catcher_y, channel)
                        out_path = os.path.join(processed_dir, cropped_image_name)
                        try:
                            to_save = total_stack[:, :, channel_number-1, 
                                                      catcher_y-crop_window_h//2:catcher_y+crop_window_h//2,
                                                      catcher_x-crop_window_w//2:catcher_x+crop_window_w//2]
                        except: 
                            to_save = total_stack[:, :, channel_number-1, 
                                                      catcher_y-crop_window_h//2:catcher_y+crop_window_h//2-28,
                                                      catcher_x-crop_window_w//2:catcher_x+crop_window_w//2-28]

                        tifffile.imsave(filename=out_path,
                                        data=np.squeeze(to_save))
                    except:
                        pass
            
if __name__ == '__main__':
    main()