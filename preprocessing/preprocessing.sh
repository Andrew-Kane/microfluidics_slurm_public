#!/bin/bash

#SBATCH -n 1
#SBATCH -t 0-04:00
#SBATCH -p serial_requeue
#SBATCH --mem-per-cpu=1000
#SBATCH -o %A_%a.out
#SBATCH -e %A_%a.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=andrewkane@g.harvard.edu

img_dir=$1

source new-modules.sh
module load Anaconda3/2.1.0-fasrc01
source activate PYTO_SEG_ENV
module load fiji/1.49j-fasrc01

python3 ~/code/microfluidics_slurm/preprocessing/preprocessing.py -d $img_dir
