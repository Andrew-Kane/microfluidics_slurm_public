import os
import sys
sys.path.append('/n/home06/akane/code')
import argparse
from microfluidics import Segment


parser = argparse.ArgumentParser(description = 'Segment cells from \
                                 images and return pickled objects.')
parser.add_argument('-d', '--img_dir', required = True, 
                    help = 'directory containing images to segment.')
parser.add_argument('-t', '--threshold', required = True,
                    help = 'threshold for segmentation.')
parser.add_argument('-n', '--array_number', required = True,
                    help = 'the job number within the job array.')
parser.add_argument('-a', '--array_length', required = True,
                    help = 'length of the job array.')

args = parser.parse_args()
print(args)
img_dir = args.img_dir
threshold = int(args.threshold)
array_n = int(args.array_number)
array_l = int(args.array_length)

def main():
    os.chdir(os.path.join(img_dir,'fluorescence_analysis'))
    flist = os.listdir()
    imgs = [f for f in flist if '.tif' in f.lower()]
    seg_imgs = [im for im in imgs if 'segment' in im.lower()]
    seg_imgs.sort()
    ims_per_job = int(len(seg_imgs)/array_l)
    split_seg_list = []
    for i in range(0, len(seg_imgs), ims_per_job):
        split_seg_list.append(seg_imgs[i:i+ims_per_job])
    n_leftover = len(seg_imgs)%array_l
    if n_leftover != 0:
        leftover_seg = seg_imgs[-n_leftover:]
        for x in range(0,len(leftover_seg)):
            split_seg_list[x].append(leftover_seg[x])
    seg_list = split_seg_list[array_n]
    print('Segment images:')
    print(seg_list)
    for i in range(0,len(seg_list)):
        os.chdir(img_dir)
        print('SEGMENTING ' + seg_list[i])
        segmenter = Segment.Segmenter(seg_list[i],
                                               threshold = threshold)
        seg_obj = segmenter.segment()
        seg_obj.pickle(output_dir = img_dir + '/pickles')
        os.chdir(img_dir)
        del seg_obj

if __name__ == '__main__':
    main()
