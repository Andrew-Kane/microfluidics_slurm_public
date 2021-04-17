# microfluidics_slurm_public
Submission scripts for image pre-processing, [microlfuidics](https://github.com/Andrew-Kane/microfluidics_public/) segmentation, and post-segmentation analysis on Harvard's Odyssey cluster

Authors: Andrew Kane, andrew_kane[at]fas[dot]harvard[dot]edu

__Note:__ These scripts are currently designed for running on Andrew's personal RC account, and will require some fiddling with paths and other preparation to make it work for you. Ask me if you need help.

## Puropse:
These scripts was written to correlate _S. cerevisiae_ lifespan and age with fluorescence intensity given by whatever reporter the user has provided.

The scripts take raw image files obtained on a microscope and crop them down to individual catchers using proprietary code provided by Calico Labs which is not provided here. Cells segmented by [DeepCell](https://github.com/CovertLab/DeepCell/) are used to generate masks:

![image](https://user-images.githubusercontent.com/29231831/115124326-85de2500-9f8f-11eb-8a55-eb53ecfa9f11.png)

Assuming the mother cell is the center cell with the largest volume (this should be confirmed by the user and only suitable images should be provided), a mother cell mask is generated and applied to fluorescent images. Intensity of fluorescence from these masked images is combined with an annotation json file (created using proprietary code provided by Calico Labs which is not provided here) and output into one dataframe:

![image](https://user-images.githubusercontent.com/29231831/115124428-32200b80-9f90-11eb-852c-287f55328228.png)


## Contents:
Three sets of scripts contained in separate sub-directories:

__preprocessing:__ For pre-segmentation and pre-annotation processing of images acquired TE-2000 epifluorescence microscopy.
- preprocessing.sh and .py: for automatically sorting all images taken over a timecourse into inidivual folders for each stage position and individual subfolders for each wavelength captured.

__segmentation:__ For performing segmentation on fluorescence microscopy images using pyto_segmenter. See the scripts for command-line arguments.
- seg.sh and .py: for segmenting cell objects output by [DeepCell](https://github.com/CovertLab/DeepCell/). Outputs only _S. cerevisiae_ mother cell masks. Inputs are video files in the form of Z-stack tiffs cropped down to individual catchers by proprietary code provided by Calico Labs which is not provided here and segmented by DeepCell. Preselection by the user must be done for cells with mother cells in the center of the catcher for the entire duration of their lifespan.

__analysis__: For post-segmentation analysis of segmented _S. cerevisiae_ mother cells.
- analysis.sh and .py: for creating dataframes to correlate _S. cerevisiae_ cell age, lifespan, volume and fluorescence intensity from a reporter. Inputs include a lifespan annotation json file created using propriety code, video files in the form of Z-stack tiffs cropped down to individual catchers by prorietary code, and fluorescence video files in the form of Z-stak tiffs cropped down to the individual catchers by proprietary code. Proprietary code was provided by Calico Labs which is not provided here.

## Running analysis on the Odyssey cluster

Before you can run analysis on the cluster, you'll need to set up an environment using Python 3 (all of our segmentation and analysis scripts are implemented in Python 3). You can find general instructions for getting this up and running [here](https://www.rc.fas.harvard.edu/resources/documentation/software-on-odyssey/python/). Specifically, you'll need to do the following:

1. log in to the cluster
2. `cd ~`  
to navigate to your home folder
3. `module load Anaconda3/2.1.0-fasrc01`  
to switch to Python 3 (with most packages - numpy, scipy, scikit-image, matplotlib, pandas, etc. - already implemented)
4. `conda create -n PYTO_SEG_ENV --clone="$PYTHON_HOME"`  
This will create a new "python environment" called PYTO_SEG_ENV. We need to do this because we need to update a few python packages beyond what's currently installed on the cluster.
5. `source activate PYTO_SEG_ENV`  
This will activate the new python environment you just made.
6. `conda install numpy`  
to update to the newest version of numpy (the one installed here is a couple of updates behind, and I had to use functions from a newer version of python)
7. `conda install scikit-image`  
to update to the newest version of scikit-image, which has a bunch of image file loading and saving functions that we use. The old version on the cluster can't handle some of the file formats we use. This will take a while because it needs to update a whole bunch of other packages.
8. Set up your account so that it automatically activates your python environment every time you log into the cluster. This way you don't need to do it every time you log in before running our scripts.
    1. If you're not already there, switch to your home folder:  
    `cd ~`
    2. Open up your .bash_profile file, which tells the cluster what to do upon startup:  
    `vim .bash_profile`  
    __note:__ _You're going to be making these changes using a text editor called Vim. Because you can't use programs with a GUI (e.g. Atom, RStudio, MatLab, etc.) on the cluster, you'll want to get used to using Vim to make small edits to scripts. It's un-intuitive but great once you familiarize yourself. See http://vim.wikia.com/wiki/Tutorial for a tutorial._
    3. Navigate to the end of the file and add the following two lines:  
    `module load Anaconda3/2.1.0-fasrc01`  
    `source activate PYTO_SEG_ENV`  
    4. Save the file (press Esc to exit insert mode, then type :wq and hit Enter)


Last updated: 4.17.2021
