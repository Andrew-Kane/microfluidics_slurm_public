#!/bin/bash

#SBATCH -n 1
#SBATCH -t 0-04:00
#SBATCH -p serial_requeue
#SBATCH --mem-per-cpu=1000
#SBATCH -o %A_%a.out
#SBATCH -e %A_%a.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nweir@fas.harvard.edu

data_dir=$1
experiment_name=$2
top=$3
bottom=$4
left=$5
right=$6
position=$7

source new-modules.sh
module load Anaconda3/2.1.0-fasrc01
source activate PYTO_SEG_ENV
module load fiji/1.49j-fasrc01

python3 ~/code/microfluidics_slurm/preprocessing/assign_catcher.py -d $data_dir $experiment_name $top $bottom $left $right $position

