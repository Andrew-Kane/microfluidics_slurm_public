#!/bin/bash

#SBATCH -n 1
#SBATCH -t 0-04:00
#SBATCH -p serial_requeue
#SBATCH --mem-per-cpu=1500
#SBATCH -o %A_%a.out
#SBATCH -e %A_%a.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=andrewkane@g.harvard.edu

img_dir=$1
experiment_name=$2
ntasks=$3
source new-modules.sh
source activate PYTO_SEG_ENV

cd $img_dir
python3 ~/code/microfluidics_slurm/analysis/analysis.py -d $img_dir -e $experiment_name \
    -n $SLURM_ARRAY_TASK_ID -a $ntasks
