#!/bin/bash

#SBATCH -n 1
#SBATCH -t 0-04:00
#SBATCH -p serial_requeue
#SBATCH --mem-per-cpu=1500
#SBATCH -o %A_%a.out
#SBATCH -e %A_%a.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=andrewkane@g.harvard.edu

data_dir=$1
experiment_name=$2
ntasks=$3
source new-modules.sh
source activate PYTO_SEG_ENV

cd $img_dir
python3 ~/code/microfluidics_slurm/saving/crop_and_save.py -d $data_dir -n $experiment_name \
	-a $SLURM_ARRAY_TASK_ID -l $ntasks
